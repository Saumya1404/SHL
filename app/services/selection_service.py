from typing import List,Dict
from app.services.intent_service import Intent
from collections import Counter

def is_technical(candidate: Dict, intent: Intent) -> bool:
    text = f"{candidate.get('name','')} {candidate.get('description','')}".lower()
    return any(skill in text for skill in intent.core_technical_skills)


def is_behavioral(candidate: Dict) -> bool:
    return any(
        t in candidate.get("test_type", [])
        for t in ["Personality & Behavior", "Competencies"]
    )


def duration_ok(candidate: Dict, intent: Intent) -> bool:
    if intent.max_duration_minutes is None:
        return True
    duration = candidate.get("duration")
    return (duration is None) or (duration <= intent.max_duration_minutes)



def redundancy_penalty(candidate:Dict, selected:List[Dict])->float:
    penalty = 0.0
    for s in selected:
        overlap = set(candidate.get("test_type", [])) & set(s.get("test_type", []))
        penalty += 0.2*len(overlap)

        name_tokens_c = set(candidate.get("name","").lower().split())
        name_tokens_s = set(s.get("name","").lower().split())
        penalty += 0.1*len(name_tokens_c & name_tokens_s)
    return penalty


def select_assessments(candidates: List[Dict], intent: Intent,k: int=5) -> List[Dict]:
    selected:List[Dict] =[]
    used_ids = set()
    
    if intent.max_duration_minutes is not None:
        candidates = [
            c for c in candidates
            if (c.get("duration") is None) or (c.get("duration") <= intent.max_duration_minutes)
        ]
        
    pool = [ c for c in candidates if duration_ok(c,intent)]
    if not pool:
        return []
    tech_targets = 0
    behav_targets = 0

    if intent.needs_balance:
        tech_targets= int(0.6*k)
        behav_targets= k - tech_targets

    elif intent.needs_technical:
        tech_targets = k
    elif intent.needs_behavioral:
        behav_targets = k

    enforce_tech = intent.technical_confidence >=0.7
    enforce_behav = intent.behavioral_confidence >=0.7

    while len(selected)<k and pool:
        best = None
        best_score = float('-inf')
        for c in pool:
            if c['id'] in used_ids:
                continue
            score = c.get("rerank_score",0.0)

            tech_count = sum(is_technical(x,intent) for x in selected)
            behav_count = sum(is_behavioral(x) for x in selected)

            if is_technical(c,intent) and tech_count<tech_targets:
                score += 0.3
            if is_behavioral(c) and behav_count<behav_targets:
                score +=0.3

            if enforce_tech and tech_count == 0 and not is_technical(c,intent):
                score -= 2.0
            if enforce_behav and behav_count == 0 and not is_behavioral(c):
                score -= 1.0

            score -= redundancy_penalty(c, selected)

            if score > best_score:
                best = c
                best_score = score

        if best is None:
            break
        selected.append(best)
        used_ids.add(best['id'])
        pool.remove(best)
    return selected
