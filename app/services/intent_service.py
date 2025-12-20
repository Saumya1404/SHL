from dataclasses import dataclass
import re
from typing import List, Optional


@dataclass
class Intent:
    technical_skills: List[str]
    behavioral_skills: List[str]

    needs_technical: bool
    needs_behavioral: bool
    needs_balance: bool

    max_duration_minutes: Optional[int]

    technical_confidence: float
    behavioral_confidence: float

TECHNICAL_KEYWORDS = {
    "java", "python", "sql", "developer", "engineering", "software",
    "programming", "technical", "coding", "it", "cloud"
}

BEHAVIORAL_KEYWORDS = {
    "leadership", "collaboration", "communication", "interpersonal",
    "people management", "culture", "cultural", "values",
    "teamwork", "stakeholder", "business teams", "soft skills"
}


def extract_duration_minutes(query:str)->Optional[int]:
    match = re.search(r"(\d+)\s*(minute|min|mins)", query)
    if match:
        return int(match.group(1))

    match = re.search(r"(\d+)\s*(hour|hr|hrs)", query)
    if match:
        return int(match.group(1)) * 60
    if "hour" in query:
        return 60
    return None

def detect_skills(text: str):
    text_lower = text.lower()

    technical_hits = [
        kw for kw in TECHNICAL_KEYWORDS
        if kw in text_lower
    ]

    behavioral_hits = [
        kw for kw in BEHAVIORAL_KEYWORDS
        if kw in text_lower
    ]

    return technical_hits, behavioral_hits

def parse_intent(query:str)->Intent:
    max_duration = extract_duration_minutes(query)
    technical_skills, behavioral_skills = detect_skills(query)
    needs_technical = len(technical_skills) > 0
    needs_behavioral = len(behavioral_skills) > 0
    needs_balance = needs_technical and needs_behavioral
    technical_confidence = min(1.0, 0.3 + 0.2 * len(technical_skills)) if needs_technical else 0.0
    behavioral_confidence = min(1.0, 0.3 + 0.2 * len(behavioral_skills)) if needs_behavioral else 0.0
    return Intent(
        technical_skills=list(set(technical_skills)),
        behavioral_skills=list(set(behavioral_skills)),
        needs_technical=needs_technical,
        needs_behavioral=needs_behavioral,
        needs_balance=needs_balance,
        max_duration_minutes=max_duration,
        technical_confidence=technical_confidence,
        behavioral_confidence=behavioral_confidence,
    )




    