# app/schemas/output.py
from pydantic import BaseModel
from typing import List

class ViolationReport(BaseModel):
    violation_type: str            # نوع المخالفة
    violation_severity: str        # Low | Medium | High
    people_count: int              # عدد الأشخاص
    detected_objects: List[str]    # الأشياء الظاهرة
    confidence: float              # الثقة

