import hashlib
from pathlib import Path
import logging
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from config import VECTORSTORE_DIR, EMBEDDING_MODEL

logging.basicConfig(level=logging.INFO)

class VectorStoreService:
    def __init__(self):
        # استخدام موديل الـ Embeddings
        self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        self.loaded_vectorstores = {}

    def _safe_name(self, name: str) -> str:
        return hashlib.md5(name.encode("utf-8")).hexdigest()

    def load_or_create(self, pdf_path: str, name: str):
        safe_name = self._safe_name(name)
        store_path = VECTORSTORE_DIR / safe_name
        
        # 1. إذا كانت قاعدة البيانات موجودة، قم بتحميلها كـ VectorStore
        if store_path.exists() and (store_path / "index.faiss").exists():
            logging.info(f"🔄 تحميل قاعدة البيانات الموجودة مسبقاً: {name}")
            vs = FAISS.load_local(
                str(store_path), 
                self.embeddings, 
                allow_dangerous_deserialization=True
            )
            return vs 

        # 2. إذا لم تكن موجودة، نقوم بمعالجة الملف من جديد
        if not Path(pdf_path).exists():
            raise FileNotFoundError(f"❌ لم يتم العثور على الملف في المسار: {pdf_path}")

        store_path.mkdir(parents=True, exist_ok=True)
        
        try:
            logging.info(f"📄 جاري معالجة ملف PDF جديد: {pdf_path}")
            loader = PyPDFLoader(pdf_path)
            docs = loader.load()
            
            # --- التعديل الجوهري هنا ---
            # تم تحسين المقسمات (Separators) لتناسب اللائحة المحملة:
            # - "\nالمادة": لضمان فصل المواد القانونية بشكل نظيف.
            # - "\n•": للحفاظ على جدول المخالفات في نهاية الملف (كل نقطة هي مخالفة وغرامتها).
            # - زيادة الـ chunk_size لاستيعاب الجمل القانونية الطويلة.
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, 
                chunk_overlap=150,
                separators=[
                    "\nالمادة", 
                    "\n•", 
                    "\n\n", 
                    ".\n", 
                    "\n", 
                    " "
                ] 
            )
            chunks = splitter.split_documents(docs)

            logging.info(f"🏗️ جاري إنشاء VectorStore لـ {len(chunks)} قطعة نصية...")
            
            # بناء الفهرس وحفظه محلياً
            vs = FAISS.from_documents(chunks, self.embeddings)
            vs.save_local(str(store_path))
            
            logging.info(f"✅ تم إنشاء وحفظ قاعدة البيانات بنجاح: {name}")
            return vs
            
        except Exception as e:
            logging.error(f"❌ فشل في إنشاء VectorStore: {e}")
            return None

vectorstore_service = VectorStoreService()