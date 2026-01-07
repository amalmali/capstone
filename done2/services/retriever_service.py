from services.vectorstore_service import vectorstore_service

retrievers = {}

def register_pdf(name: str, path: str):
    vs = vectorstore_service.load_or_create(path, name)
    retrievers[name] = vs.as_retriever(search_kwargs={"k": 3})

def retrieve(name: str, query: str) -> str:
    docs = retrievers[name].invoke(query)
    return "\n\n".join(d.page_content for d in docs)
