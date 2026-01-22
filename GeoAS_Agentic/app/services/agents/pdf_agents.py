# services/agents/pdf_agents.py

from typing import Optional, Tuple
from services.rag_service import answer
from services.agents.context_agent import build_zone_aware_query

# مفاتيح الـ PDF (نفس المستخدمة في المشروع)
GENERAL_RULES_KEY = "مشروع اللائحة التنفيذية للمناطق المحمية"
PROTECTED_RULES_KEY = "protected_areas_rules"


class ProtectedAreasAgent:
    """
    Agent مختص فقط بالمحميات (داخل نطاق محمي).
    - يستخدم protected_areas_rules
    - يقيّد السؤال حسب مستوى الحماية
    """

    key = PROTECTED_RULES_KEY

    def handle(
        self,
        query: str,
        protection_level: Optional[str]
    ) -> Tuple[str, str]:

        enriched_query = build_zone_aware_query(query, protection_level)
        return answer(enriched_query, self.key)


class GeneralLawAgent:
    """
    Agent مختص بالمعلومات العامة (خارج المحميات).
    """

    key = GENERAL_RULES_KEY

    def handle(self, query: str) -> Tuple[str, str]:
        return answer(query, self.key)


# (اختياري – للتأكد أن الملف يُحمّل)
print("✅ pdf_agents loaded successfully")