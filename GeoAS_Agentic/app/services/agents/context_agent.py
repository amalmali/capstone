# services/agents/context_agent.py

from typing import Optional

def build_zone_aware_query(user_query: str, protection_level: Optional[str]) -> str:
    level_map = {
        "low": "المناطق ذات الحماية المنخفضة",
        "medium": "المناطق ذات الحماية المتوسطة",
        "high": "المناطق ذات الحماية العالية"
    }

    if not protection_level:
        return user_query

    section_name = level_map.get(str(protection_level).lower())
    if not section_name:
        return user_query

    return (
        f"أجب فقط بالاعتماد على قسم \"{section_name}\" من المرجع.\n\n"
        f"السؤال: {user_query}"
    )


def prepend_location_context(
    response_text: str,
    zone_name: Optional[str],
    protection_level: Optional[str]
) -> str:
    if not zone_name or not protection_level:
        return response_text

    level_map = {
        "low": "منخفضة",
        "medium": "متوسطة",
        "high": "عالية"
    }

    level_ar = level_map.get(str(protection_level).lower(), protection_level)

    return (
        f"بحسب تواجدك في محمية {zone_name} "
        f"ذات مستوى الحماية {level_ar}:\n\n"
        + response_text
    )