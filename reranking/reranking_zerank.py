from zeroentropy import ZeroEntropy
from typing import List,Dict
zclient = ZeroEntropy()

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
        idx = result.index,
        candidates[idx]['zerank_score'] = result.relevance_score

    return sorted(
        candidates,
        key=lambda c: c.get('zerank_score', 0),
        reverse=True
    )
