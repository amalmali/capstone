from services.vectorstore_service import vectorstore_service
import logging


retrievers = {}

def register_pdf(name: str, path: str):
    """
    تسجيل ملف PDF وتحويله إلى محرك بحث سريع.
    تم رفع عدد النتائج المسترجعة (k) لضمان جلب المخالفة مع قيمة الغرامة.
    """
    try:
        
        vs = vectorstore_service.load_or_create(path, name)
        
        if vs:
            
            retrievers[name] = vs.as_retriever(
                search_type="similarity",
                search_kwargs={
                    "k": 6  
                }
            )
            logging.info(f"✅ تم إنشاء محرك استرجاع سريع للملف: {name} بنجاح (k=6)")
        else:
            logging.error(f"❌ فشل إنشاء الـ VectorStore للملف: {name}")
            
    except Exception as e:
        logging.error(f"❌ خطأ فني أثناء تسجيل ملف PDF: {e}")

def retrieve(name: str, query: str) -> str:
    """
    استرجاع النصوص المتعلقة بالسؤال وتنسيقها بشكل يسهل على الموديل قراءته.
    """
    if name not in retrievers:
        logging.warning(f"⚠️ المحرك {name} غير مسجل حالياً.")
        return ""
    
    try:
        
        docs = retrievers[name].invoke(query)
        
        if not docs:
            logging.info(f"ℹ️ لم يتم العثور على نتائج مطابقة لـ: {query}")
            return ""

        
        context_parts = []
        for i, d in enumerate(docs):
            content = d.page_content.strip()
            context_parts.append(f"--- جزء قانوني مستخرج ({i+1}) ---\n{content}")
            
        return "\n\n".join(context_parts)
        
    except Exception as e:
        logging.error(f"❌ خطأ أثناء استرجاع البيانات: {e}")
        return ""