import os
import re
from typing import List

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


#path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # rag/
PROJECT_DIR = os.path.dirname(BASE_DIR)                # voice_app/
DATA_DIR = os.path.join(PROJECT_DIR, "data")           # voice_app/data
INDEX_DIR = os.path.join(DATA_DIR, "faiss_index")      # voice_app/data/faiss_index

PDF_PATH = os.path.join(DATA_DIR, "مشروع اللائحة التنفيذية للمناطق المحمية.pdf")

#Embeddings
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


# cleaning text

def clean_text(text: str) -> str:
    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)

    replacements = {
        "ﻓﻲ": "في",
        "اﻟ": "ال",
        "ﻟﻠ": "لل",
        "ﺗ": "ت",
        "ﺻ": "ص",
        "ﺔ": "ة",
        "ﺄ": "أ",
        "ﺇ": "إ",
        "ﺍ": "ا",
        "ﺎ": "ا",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)

    return text.strip()


# FAISS

_embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
_vector_store = None

def _build_index():
    print("Building FAISS index from PDF...")

    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(f" PDF file not found: {PDF_PATH}")

    loader = PyPDFLoader(PDF_PATH)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=300
    )
    chunks = splitter.split_documents(documents)

    for c in chunks:
        c.page_content = clean_text(c.page_content)

    vector_store = FAISS.from_documents(chunks, _embeddings)

    os.makedirs(INDEX_DIR, exist_ok=True)
    vector_store.save_local(INDEX_DIR)

    print("FAISS index built and saved.")
    return vector_store


def _load_index():
    global _vector_store

    if _vector_store is not None:
        return _vector_store

    index_file = os.path.join(INDEX_DIR, "index.faiss")

    if not os.path.exists(INDEX_DIR) or not os.path.exists(index_file):
        print("FAISS index not found. Rebuilding...")
        _vector_store = _build_index()
    else:
        print(" Loading existing FAISS index...")
        _vector_store = FAISS.load_local(
            INDEX_DIR,
            _embeddings,
            allow_dangerous_deserialization=True
        )

    return _vector_store



# RAG

def retrieve_context(query: str, k: int = 5) -> List[str]:
    if not query or not query.strip():
        return []

    vector_store = _load_index()

    results = vector_store.similarity_search(query, k=k)

    contexts = []
    for doc in results:
        text = clean_text(doc.page_content)
        contexts.append(text[:1000])

    return contexts
