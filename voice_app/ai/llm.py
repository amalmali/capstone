import ollama

MODEL_NAME = "llama3"

def llama_answer(question, context):
    prompt = f"""
أنت مساعد ذكي متخصص في الأنظمة البيئية والمناطق المحمية في المملكة العربية السعودية.
استخدم المعلومات التالية فقط للإجابة على السؤال.
أجب باللغة العربية الفصحى وبأسلوب واضح ومختصر.

المحتوى:
{context}

السؤال:
{question}

الإجابة:
"""


    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}]
    )

    return response["message"]["content"]
