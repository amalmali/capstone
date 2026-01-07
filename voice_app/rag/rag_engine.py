from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

PDF_PATH = "data/مشروع اللائحة التنفيذية للمناطق المحمية.pdf"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
TOP_K = 4

def read_pdf_text(path: str) -> str:
    reader = PdfReader(path)
    text = []
    for page in reader.pages:
        t = page.extract_text()
        if t:
            text.append(t)
    return "\n".join(text)

def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    chunks = []
    i = 0
    while i < len(text):
        chunks.append(text[i:i+size])
        i += max(1, size - overlap)
    return chunks

# تحميل النص وبناء الفهرس مرة واحدة
doc_text = read_pdf_text(PDF_PATH)
chunks = chunk_text(doc_text)

embedder = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
embeddings = embedder.encode(chunks, normalize_embeddings=True)
embeddings = np.array(embeddings).astype("float32")

index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(embeddings)

def retrieve_context(question: str, top_k=TOP_K):
    q_emb = embedder.encode([question], normalize_embeddings=True)
    q_emb = np.array(q_emb).astype("float32")
    _, idxs = index.search(q_emb, top_k)
    return [chunks[i] for i in idxs[0] if i != -1]
