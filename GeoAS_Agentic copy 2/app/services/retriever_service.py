# retriever_service.py
from services.vectorstore_service import vectorstore_service
import logging

# قاموس لتخزين الـ retrievers الجاهزة في الذاكرة
retrievers = {}

def _normalize_key(name: str) -> str:
    """
    (FIX) توحيد الاسم لتجنب مشاكل:
    - protected_areas_rules.pdf vs protected_areas_rules
    - مسافات زائدة
    """
    if not name:
        return ""
    name = name.strip()
    if name.lower().endswith(".pdf"):
        name = name[:-4]
    return name

def register_pdf(name: str, path: str):
    """
    تسجيل ملف PDF وتحويله إلى محرك بحث سريع.
    تم رفع عدد النتائج المسترجعة (k) لضمان جلب المخالفة مع قيمة الغرامة.
    """
    try:
        name = _normalize_key(name)

        # 1. استدعاء الخدمة لتحميل أو إنشاء الـ VectorStore (FAISS)
        vs = vectorstore_service.load_or_create(path, name)

        if vs:
            # 2. تحويل الـ VectorStore إلى Retriever
            retrievers[name] = vs.as_retriever(
                search_type="similarity",
                search_kwargs={
                    "k": 1
                }
            )
            logging.info(f"✅ تم إنشاء محرك استرجاع سريع للملف: {name} بنجاح (k=1)")
        else:
            logging.error(f"❌ فشل إنشاء الـ VectorStore للملف: {name}")

    except Exception as e:
        logging.error(f"❌ خطأ فني أثناء تسجيل ملف PDF: {e}")

def retrieve(name: str, query: str) -> str:
    """
    استرجاع النصوص المتعلقة بالسؤال وتنسيقها بشكل يسهل على الموديل قراءته.
    """
    name = _normalize_key(name)

    if name not in retrievers:
        logging.warning(f"⚠️ المحرك {name} غير مسجل حالياً. المتاح: {list(retrievers.keys())}")
        return ""

    try:
        # تنفيذ عملية البحث
        docs = retrievers[name].invoke(query)

        if not docs:
            logging.info(f"ℹ️ لم يتم العثور على نتائج مطابقة لـ: {query}")
            return ""

        # تنسيق النصوص مع ترقيم الأجزاء لمساعدة الموديل في الفصل بين المواد
        context_parts = []
        for i, d in enumerate(docs):
            content = (d.page_content or "").strip()
            context_parts.append(f"--- جزء قانوني مستخرج ({i+1}) ---\n{content}")

        return "\n\n".join(context_parts)

    except Exception as e:
        logging.error(f"❌ خطأ أثناء استرجاع البيانات: {e}")
        return ""