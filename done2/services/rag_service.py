from services.retriever_service import retrieve
from services.llm_service import generate
from services.memory_service import memory_service

PROMPT = """
أنت مساعد ذكي.
أجب فقط باستخدام المعلومات التالية.
استخدم سجل المحادثة لفهم السؤال.
إذا لم تجد الإجابة قل: "لا توجد معلومات كافية".

سجل المحادثة:
{history}

المعلومات:
{context}

السؤال:
{question}
"""

def answer(query: str, pdf_name: str, session_id: str):
    memory = memory_service.get(session_id)
    history = memory.load_memory_variables({}).get("history", "")

    context = retrieve(pdf_name, query)

    prompt = PROMPT.format(
        history=history,
        context=context,
        question=query
    )

    response = generate(prompt)

    memory.save_context(
        {"input": query},
        {"output": response}
    )

    return response, context
