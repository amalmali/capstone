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
        # لا نحمّل الموديل عند init
        self.embeddings = None
        self.model_name = EMBEDDING_MODEL
        self.loaded_vectorstores = {}
        logging.info("VectorStoreService initialized (embeddings not loaded yet)")

    def get_embeddings(self):
        """تحميل Embeddings عند أول استخدام"""
        if self.embeddings is None:
            try:
                logging.info(f"⏳ Loading HuggingFace Embeddings: {self.model_name} ...")
                self.embeddings = HuggingFaceEmbeddings(model_name=self.model_name)
                logging.info("✅ HuggingFace Embeddings loaded successfully")
            except Exception as e:
                logging.error(f"❌ Failed to load embeddings: {e}")
                self.embeddings = None
        return self.embeddings

    def _safe_name(self, name: str) -> str:
        return hashlib.md5(name.encode("utf-8")).hexdigest()

    def load_or_create(self, pdf_path: str, name: str):
        # التأكد من تحميل Embeddings
        embeddings = self.get_embeddings()
        if embeddings is None:
            logging.error("❌ لا يمكن إنشاء VectorStore بدون Embeddings")
            return None

        safe_name = self._safe_name(name)
        store_path = VECTORSTORE_DIR / safe_name
        
        # 1. إذا كانت قاعدة البيانات موجودة، قم بتحميلها
        if store_path.exists() and (store_path / "index.faiss").exists():
            try:
                logging.info(f"🔄 تحميل قاعدة البيانات الموجودة مسبقاً: {name}")
                vs = FAISS.load_local(
                    str(store_path), 
                    embeddings, 
                    allow_dangerous_deserialization=True
                )
                return vs
            except Exception as e:
                logging.error(f"❌ فشل في تحميل VectorStore موجود: {e}")
                # إذا فشل التحميل، نستمر لإنشاء جديد

        # 2. إذا لم تكن موجودة، نقوم بمعالجة الملف
        if not Path(pdf_path).exists():
            logging.error(f"❌ لم يتم العثور على الملف في المسار: {pdf_path}")
            return None

        store_path.mkdir(parents=True, exist_ok=True)
        
        try:
            logging.info(f"📄 جاري معالجة ملف PDF جديد: {pdf_path}")
            loader = PyPDFLoader(pdf_path)
            docs = loader.load()
            
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

            vs = FAISS.from_documents(chunks, embeddings)
            vs.save_local(str(store_path))
            
            logging.info(f"✅ تم إنشاء وحفظ قاعدة البيانات بنجاح: {name}")
            return vs
            
        except Exception as e:
            logging.error(f"❌ فشل في إنشاء VectorStore: {e}")
            return None

# إنشاء instance ولكن بدون تحميل الموديل بعد
vectorstore_service = VectorStoreService()
