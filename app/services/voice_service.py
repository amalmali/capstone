from services.audio_utils import listen_to_mic, speak_text
from services.rag_service import answer
from services.retriever_service import retrievers
import time

def start_voice_assistant_standalone():
    """وظيفة للتشغيل التجريبي عبر الكونسول بنظام الضغط للبدء"""
    print("✅ نظام المساعدة الصوتي جاهز (نمط Push-to-Talk التجريبي)...")
    speak_text("أهلاً بك، كيف يمكنني مساعدتك؟")
    
    while True:
        input("\nاضغط Enter لبدء التحدث...")
        query = listen_to_mic()
        
        if query:
            print(f"🎤 سمعت: {query}")
            if any(word in query for word in ["خروج", "إيقاف", "انهاء"]):
                speak_text("مع السلامة.")
                break
                
            if retrievers:
                pdf_name = list(retrievers.keys())[0]
                response, _ = answer(query, pdf_name)
                print(f"🤖 الرد: {response}")
                speak_text(response)
            else:
                print("Error: No PDF loaded.")
        else:
            print("⚠️ لم يتم التقاط صوت واضح.")

if __name__ == "__main__":
    time.sleep(2) 
    start_voice_assistant_standalone()