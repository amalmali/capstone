# services/agents/agent_router.py

from typing import Dict, Any
from fastapi import Request

from services.rag_service import detect_intent
from services.agents.location_agent import LocationAgent
from services.agents.permission_agent import PermissionAgent
from services.agents.pdf_router_agent import PDFRouterAgent
from services.agents.context_agent import prepend_location_context
from services.retriever_service import retrievers  # ✅ مهم لتفعيل metadata


class AgentRouter:
    """
    AgentRouter هو العقل الرئيسي للنظام.
    - يحدد الموقع
    - يختار PDF Agent المناسب
    - يحدد نية السؤال
    - ينسق الإجابة النهائية
    """

    def __init__(self):  # ✅ تصحيح مهم (كان مكتوب _init_)
        self.location_agent = LocationAgent()
        self.permission_agent = PermissionAgent()
        self.pdf_router = PDFRouterAgent()

    def route_text(self, request: Request, query: str) -> Dict[str, Any]:
        # --------------------------------------------------
        # 1️⃣ القرار المكاني
        # --------------------------------------------------
        location = self.location_agent.get_location(request)

        inside = location["inside"]
        zone_name = location["zone_name"]
        protection_level = location["protection_level"]


        # --------------------------------------------------
        # ✅ تفعيل metadata: تمرير مستوى الحماية للـ RAG
        # --------------------------------------------------
        retrievers["_current_protection_level"] = protection_level

        # --------------------------------------------------
        # 2️⃣ اختيار Agent الـ PDF المناسب
        # --------------------------------------------------
        pdf_agent = self.pdf_router.route(inside)

        # --------------------------------------------------
        # 3️⃣ تحديد نية السؤال
        # --------------------------------------------------
        intent = detect_intent(query)

        # --------------------------------------------------
        # 4️⃣ تنفيذ الـ Agent المناسب
        # --------------------------------------------------
        if intent == "permission":
            response, _ = self.permission_agent.handle(
                query=query,
                pdf_agent=pdf_agent,
                protection_level=protection_level
            )
        else:
            if inside:
                response, _ = pdf_agent.handle(query, protection_level)
            else:
                response, _ = pdf_agent.handle(query)

        # --------------------------------------------------
        # 5️⃣ إضافة السياق المكاني (اختياري)
        # --------------------------------------------------
        if inside and zone_name and protection_level and response:
            response = prepend_location_context(
                response,
                zone_name,
                protection_level
            )

        # --------------------------------------------------
        # 6️⃣ إخراج موحد للواجهة
        # --------------------------------------------------
        return {
            "response": response or "لم يتم العثور على إجابة مناسبة.",
            "inside_geofence": bool(inside),
            "zone_name": zone_name,
            "protection_level": protection_level,
            "intent": intent,
        }


# (اختياري للتأكد من التحميل)
print("✅ AgentRouter loaded successfully")