# services/agents/pdf_router_agent.py

from services.agents.pdf_agents import (
    ProtectedAreasAgent,
    GeneralLawAgent
)

class PDFRouterAgent:
    """
    مسؤول فقط عن اختيار أي PDF Agent يستخدم
    """

    def __init__(self):
        self.protected_agent = ProtectedAreasAgent()
        self.general_agent = GeneralLawAgent()

    def route(self, inside_geofence: bool):
        if inside_geofence:
            return self.protected_agent
        return self.general_agent