# services/agents/permission_agent.py

from typing import Optional, Tuple


class PermissionAgent:
    """
    Agent مختص بأسئلة:
    - هل مسموح؟
    - هل ممنوع؟
    - يجوز؟
    
    يعتمد على الـ PDF Agent المختار (محميات أو عام)
    ولا يقرر بنفسه.
    """

    def handle(
        self,
        query: str,
        pdf_agent,
        protection_level: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        يمرر السؤال للـ pdf_agent المناسب.
        """

        # لو داخل محمية (ProtectedAreasAgent)
        if hasattr(pdf_agent, "key") and pdf_agent.key == "protected_areas_rules":
            return pdf_agent.handle(query, protection_level)

        # لو خارج محمية (GeneralLawAgent)
        return pdf_agent.handle(query)


# (اختياري – للتأكد أن الملف يُحمّل)
print("✅ PermissionAgent loaded successfully")