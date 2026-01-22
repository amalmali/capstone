# services/agents/location_agent.py

from fastapi import Request
from typing import Dict, Any


class LocationAgent:
    """
    Agent مسؤول فقط عن القرار المكاني.
    - لا يتعامل مع DB
    - لا يتعامل مع RAG
    - يقرأ آخر موقع محفوظ في app.state.last_location
    """

    def get_location(self, request: Request) -> Dict[str, Any]:
        """
        يرجّع حالة الموقع الحالية بنفس الصيغة المتوقعة في بقية النظام.
        """

        # قراءة آخر موقع محفوظ (قد لا يكون موجود)
        last_location = getattr(request.app.state, "last_location", None) or {}

        return {
            "inside": bool(last_location.get("inside", False)),
            "zone_name": last_location.get("zone_name"),
            "protection_level": last_location.get("protection_level"),
        }


# (اختياري – للتأكد أن الملف يُحمّل)
print("✅ LocationAgent loaded successfully")