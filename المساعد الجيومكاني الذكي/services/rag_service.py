from services.retriever_service import retrievers
from services.llm_service import generate
import re


PROMPT_TEMPLATE = """أنت مساعد خبير في الأنظمة واللوائح السعودية.
أجب بدقة بناءً على المعلومات المرفقة فقط.
إذا لم تجد الإجابة في النص، قل "عذراً، لا تتوفر هذه المعلومة في لائحة المناطق المحمية".

السياق المستخرج من اللائحة:
{context}

السؤال:
{question}

الإجابة المباشرة:"""

def answer(query: str, pdf_name: str):
   
    retriever = retrievers.get(pdf_name)
    if not retriever:
        return "عذراً، محرك البحث القانوني غير جاهز حالياً. يرجى الانتظار لحظات.", ""

    
  
    docs = retriever.invoke(query)
    
    formatted_contexts = []
    for i, doc in enumerate(docs):
       
        text = doc.page_content
        text = re.sub(r'\s+', ' ', text)  
        text = re.sub(r'[^\w\s\.\-\(\)%٠-٩,،:]', '', text) 
        clean_content = text.strip()
        
        
        formatted_contexts.append(f"--- [الفقرة/المادة رقم {i+1}] ---\n{clean_content}")
    
    context = "\n\n".join(formatted_contexts)

    
    if not context.strip():
        return "عذراً، لم أجد نصوصاً في اللائحة الحالية تتعلق بهذا الاستفسار.", ""

    
    final_prompt = PROMPT_TEMPLATE.format(context=context, question=query)

    
    response = generate(final_prompt)
    
    
    forbidden_indicators = [
        "بناءً على فهمي", "ربما", "أعتقد", "بشكل عام", 
        "من المحتمل", "على الأرجح", "قد يكون"
    ]
    
    check_response = response.strip()
    if any(check_response.startswith(phrase) for phrase in forbidden_indicators):
        return "عذراً، التفاصيل الدقيقة لهذا السؤال غير منصوص عليها بوضوح في اللائحة المرفقة.", context

    return response.strip(), context