# services/spatial_agent.py

from services.rag_service import answer
from services.retriever_service import retrievers

# نخلي الاستيراد داخل الدالة عشان نتجنب circular import
def _generate_map():
    from services.map_service import generate_spatial_map
    return generate_spatial_map()


class SpatialAgent:
    """
    RAG Agent:
    - يجاوب باستخدام RAG
    - ويرسم خريطة في كل مرة تلقائيًا
    """

    def invoke(self, data: dict):
        user_input = (data.get("input") or "").strip()

        # =========================
        # 1) RAG Response
        # =========================
        if not user_input:
            response_text = "❌ اكتبي سؤال أو تحدثي."
        elif not retrievers:
            response_text = "⚠️ نظام اللوائح قيد التحميل..."
        else:
            pdf_name = list(retrievers.keys())[0]
            response_text, _ = answer(user_input, pdf_name)

        # =========================
        # 2) رسم الخريطة دائمًا
        # =========================
        map_path = _generate_map()

        # =========================
        # 3) الإرجاع للواجهة
        # =========================
        return {
            "output": response_text,
            "map_path": map_path
        }


agent = SpatialAgent()
