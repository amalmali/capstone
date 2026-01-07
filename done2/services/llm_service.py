from langchain_ollama import ChatOllama
from config import LLM_MODEL

llm = ChatOllama(
    model=LLM_MODEL,
    temperature=0,
    num_ctx=2048,
    num_predict=256
)

def generate(prompt: str) -> str:
    return llm.invoke(prompt).content
