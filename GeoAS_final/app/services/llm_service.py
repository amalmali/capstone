from langchain_community.chat_models import ChatOllama
import logging

def get_llm():
    """
    إعداد موديل LLM للعمل بأقصى سرعة ممكنة وبأقل استهلاك للموارد.
    """
    try:
        return ChatOllama(
            model="qwen2.5:1.5b",
            temperature=0,
         
            num_predict=150, 
            
            num_ctx=2048, 
            repeat_penalty=1.1,
           
            num_thread=8, 
        )
    except Exception as e:
        logging.error(f"❌ خطأ في تحميل موديل Ollama: {e}")
        return None


llm = get_llm()

def generate(prompt: str) -> str:
    """إرسال الـ Prompt للموديل وإرجاع النص فقط"""
    if not llm:
        return "خطأ: لم يتم تشغيل محرك الذكاء الاصطناعي."
    
    try:
        
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        logging.error(f"❌ خطأ أثناء توليد الإجابة: {e}")
        return "حدث خطأ في معالجة الإجابة."