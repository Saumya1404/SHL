from typing import List,Dict
from app.services.intent_service import Intent

def is_technical(candidate: Dict) -> bool:
    return "Knowledge & Skills" in candidate.get("test_type", [])


def is_behavioral(candidate: Dict) -> bool:
    return any(
        t in candidate.get("test_type", [])
        for t in ["Personality & Behavior", "Competencies"]
    )


def duration_ok(candidate: Dict, intent: Intent) -> bool:
    if intent.max_duration_minutes is None:
        return True
    duration = candidate.get("duration")
    return duration is None or duration <= intent.max_duration_minutes

def select_assessments(candidates: List[Dict], intent: Intent,k: int=5) -> List[Dict]:
    selected = []
    used_ids = set()
    ordered_candidates = [c for c in candidates if duration_ok(c, intent)]
    if intent.technical_confidence >= 0.7:
        for c in candidates:
            if is_technical(c) and c["id"] not in used_ids:
                selected.append(c)
                used_ids.add(c["id"])
                break
    if intent.behavioral_confidence >= 0.7:
        for c in candidates:
            if is_behavioral(c) and c["id"] not in used_ids:
                selected.append(c)
                used_ids.add(c["id"])
                break

    for c in ordered_candidates:
        if len(selected) >= k:
            break
        if c["id"] not in used_ids:
            selected.append(c)
            used_ids.add(c["id"])
    return selected