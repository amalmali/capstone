# vectorstore_service.py
import hashlib
from pathlib import Path
import logging
from unicodedata import name  # (تركته كما هو لتفادي حذف غير ضروري)

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from config import VECTORSTORE_DIR, EMBEDDING_MODEL, CHUNKS_DIR
import json


logging.basicConfig(level=logging.INFO)


class VectorStoreService:
    def __init__(self):
        # لا نحمّل الموديل عند init
        self.embeddings = None
        self.model_name = EMBEDDING_MODEL
        self.loaded_vectorstores = {}
        logging.info("VectorStoreService initialized (embeddings not loaded yet)")

    # ======================================================
    # تحميل Embeddings عند أول استخدام
    # ======================================================
    def get_embeddings(self):
        if self.embeddings is None:
            try:
                logging.info(f"⏳ Loading HuggingFace Embeddings: {self.model_name} ...")
                self.embeddings = HuggingFaceEmbeddings(model_name=self.model_name)
                logging.info("✅ HuggingFace Embeddings loaded successfully")
            except Exception as e:
                logging.error(f"❌ Failed to load embeddings: {e}")
                self.embeddings = None
        return self.embeddings

    # ======================================================
    # اسم آمن للتخزين
    # ======================================================
    def _safe_name(self, name: str) -> str:
        return hashlib.md5(name.encode("utf-8")).hexdigest()

    # ======================================================
    # حفظ Chunks في ملف JSON (مع Metadata كاملة)
    # ======================================================
    def save_chunks_to_file(self, chunks, name: str):
        output_file = CHUNKS_DIR / f"{name}_chunks.json"

        data = []
        for i, c in enumerate(chunks):
            data.append({
                "chunk_id": i + 1,
                "text": (c.page_content or "").strip(),
                # ✅ نحفظ كل الـ metadata
                "metadata": c.metadata
            })

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logging.info(f"🧩 تم حفظ {len(data)} Chunks في: {output_file}")

    # ======================================================
    # تحميل أو إنشاء VectorStore
    # ======================================================
    def load_or_create(self, pdf_path: str, name: str):
        embeddings = self.get_embeddings()
        if embeddings is None:
            logging.error("❌ لا يمكن إنشاء VectorStore بدون Embeddings")
            return None

        safe_name = self._safe_name(name)
        store_path = VECTORSTORE_DIR / safe_name

        # --------------------------------------------------
        # 1) تحميل VectorStore موجود
        # --------------------------------------------------
        if store_path.exists() and (store_path / "index.faiss").exists():
            try:
                logging.info(f"🔄 تحميل VectorStore موجود مسبقاً: {name}")
                vs = FAISS.load_local(
                    str(store_path),
                    embeddings,
                    allow_dangerous_deserialization=True
                )
                return vs
            except Exception as e:
                logging.error(f"❌ فشل تحميل VectorStore موجود: {e}")
                logging.info("♻️ سيتم إعادة إنشاء VectorStore...")

        # --------------------------------------------------
        # 2) التحقق من وجود الملف
        # --------------------------------------------------
        if not Path(pdf_path).exists():
            logging.error(f"❌ لم يتم العثور على الملف: {pdf_path}")
            return None

        store_path.mkdir(parents=True, exist_ok=True)

        try:
            logging.info(f"📄 معالجة ملف PDF: {pdf_path}")

            loader = PyPDFLoader(pdf_path)
            raw_docs = loader.load()

            # --------------------------------------------------
            # حماية من الصفحات الفارغة أو التالفة
            # --------------------------------------------------
            valid_docs = []
            for d in raw_docs:
                content = (d.page_content or "").strip()
                if len(content) > 20:
                    valid_docs.append(d)

            if not valid_docs:
                logging.error("❌ لا يوجد نص صالح داخل PDF بعد التنظيف")
                return None

            # --------------------------------------------------
            # تقسيم النص حسب نوع الـ PDF
            # --------------------------------------------------
            if name == "مشروع اللائحة التنفيذية للمناطق المحمية":
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=700,
                    chunk_overlap=50,
                    separators=[
                        "\n===",
                        "\n— الفصل",
                        "\n---",
                        "\n",
                        " "
                    ]
                )

            elif name == "protected_areas_rules":
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=700,
                    chunk_overlap=50,
                    separators=[
                        "\n===",
                        "\n—",
                        "\n",
                        " "
                    ]
                )

            else:
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=900,
                    chunk_overlap=120,
                    separators=["\n\n", "\n", " ", ""]
                )

            chunks = splitter.split_documents(valid_docs)

            # ==================================================
            # ✅ إضافة Metadata بسيطة ودلالية (خيار A)
            # ==================================================
            for c in chunks:
                text = (c.page_content or "")

                # اسم الملف
                c.metadata["pdf_name"] = name

                # رقم الصفحة
                c.metadata["page"] = c.metadata.get("page")

                # -------------------------------
                # ملف مخالفات المحميات
                # -------------------------------
                if name == "protected_areas_rules":

                    if "حماية عالية" in text:
                        c.metadata["protection_level"] = "high"
                    elif "حماية متوسطة" in text:
                        c.metadata["protection_level"] = "medium"
                    elif "حماية منخفضة" in text:
                        c.metadata["protection_level"] = "low"
                    else:
                        c.metadata["protection_level"] = "unknown"

                    if "صيد" in text:
                        c.metadata["violation_type"] = "hunting"
                    elif "رعي" in text:
                        c.metadata["violation_type"] = "grazing"
                    elif "احتطاب" in text:
                        c.metadata["violation_type"] = "logging"
                    elif "تخييم" in text:
                        c.metadata["violation_type"] = "camping"
                    elif "نار" in text:
                        c.metadata["violation_type"] = "fire"
                    else:
                        c.metadata["violation_type"] = "general"

                # -------------------------------
                # ملف اللائحة التنفيذية (العام)
                # -------------------------------
                elif name == "مشروع اللائحة التنفيذية للمناطق المحمية":

                    c.metadata["doc_type"] = "general_guidelines"

                    if "محمية" in text:
                        c.metadata["content_type"] = "reserve_info"
                    elif "التعديات" in text:
                        c.metadata["content_type"] = "violations_info"
                    elif "الأنواع" in text:
                        c.metadata["content_type"] = "biodiversity"
                    else:
                        c.metadata["content_type"] = "general"

            # --------------------------------------------------
            # تنظيف إضافي بعد التقسيم
            # --------------------------------------------------
            clean_chunks = []
            for c in chunks:
                text = (c.page_content or "").strip()
                if len(text) > 30:
                    clean_chunks.append(c)

            if not clean_chunks:
                logging.error("❌ لا يوجد Chunks صالحة بعد التقسيم")
                return None

            logging.info(f"🏗️ إنشاء VectorStore من {len(clean_chunks)} قطعة نصية")

            vs = FAISS.from_documents(clean_chunks, embeddings)
            vs.save_local(str(store_path))

            # 🧩 حفظ الـ chunks مع metadata
            self.save_chunks_to_file(clean_chunks, name)

            logging.info(f"✅ تم إنشاء وحفظ VectorStore بنجاح: {name}")
            return vs

        except Exception as e:
            logging.exception("❌ فشل إنشاء VectorStore")
            return None


# ======================================================
# Instance واحد فقط للخدمة
# ======================================================
vectorstore_service = VectorStoreService()