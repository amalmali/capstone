from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from config import VECTORSTORE_DIR, EMBEDDING_MODEL

class VectorStoreService:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL
        )
        self.vectorstores = {}

    def load_or_create(self, pdf_path: str, name: str):
        store_path = VECTORSTORE_DIR / name

        if store_path.exists():
            vs = FAISS.load_local(
                store_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            self.vectorstores[name] = vs
            return vs

        loader = PyPDFLoader(pdf_path)
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=600,
            chunk_overlap=100
        )
        chunks = splitter.split_documents(docs)

        vs = FAISS.from_documents(chunks, self.embeddings)
        store_path.mkdir(parents=True, exist_ok=True)
        vs.save_local(store_path)

        self.vectorstores[name] = vs
        return vs

vectorstore_service = VectorStoreService()
