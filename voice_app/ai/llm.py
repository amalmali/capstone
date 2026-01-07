import ollama

def llama_answer(question, contexts):

    prompt = f"""
أنت مساعد ذكي متخصص في اللوائح والأنظمة البيئية في المملكة العربية السعودية.

مهمتك:
- استخدم فقط المعلومات الموجودة في النص أدناه.
- إذا لم تجد إجابة واضحة في النص، قل: "لا توجد معلومة صريحة في اللائحة عن ذلك".
- أجب باللغة العربية فقط.
- أجب بجملة قصيرة وواضحة.
- لا تضف أي معلومات من عندك.

النص:
{contexts}

السؤال:
{question}

الإجابة:
"""

    response = ollama.generate(
        model="qwen2.5:1.5b",
        prompt=prompt
    )

    return response["response"]

