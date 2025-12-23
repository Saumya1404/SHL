from zeroentropy import ZeroEntropy
from typing import List,Dict
from dotenv import load_dotenv
import os
load_dotenv()

ZEROENTROPY_API_KEY = os.getenv("ZEROENTROPY_API_KEY")
zclient = ZeroEntropy(api_key=ZEROENTROPY_API_KEY)

def build_document(item:dict)->str:
    parts = []

    if item.get("name"):    
        parts.append(f"Title: {item['name']}")

    if item.get("description"):
        parts.append(f"Description: {item['description']}")

    if item.get("test_type"):
        parts.append(f"Type: {', '.join(item['test_type'])}")

    return "\n".join(parts)

def zerank_rerank(query:str, candidates: List[Dict])->List[Dict]:
    documents = [build_document(c) for c in candidates]
    response = zclient.models.rerank(
        model = 'zerank-2',
        query = query,
        documents = documents
    )
    for result in response.results:
        idx = getattr(result, "index", None)
        try:
            idx = int(idx)
        except Exception:
            continue

        score = getattr(result, "relevance_score", None)
        if 0 <= idx < len(candidates):
            candidates[idx]["zerank_score"] = score
            candidates[idx]["rerank_score"] = score

    return sorted(
        candidates,
        key=lambda c: c.get('zerank_score', 0),
        reverse=True
    )
