import os
import cohere 
from dotenv import load_dotenv
load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
co = cohere.Client(COHERE_API_KEY)

def _format_candidate(candidate:dict)->str:
    parts = [
        f"Name: {candidate.get('name', '')}",
        f"Description: {candidate.get('description', '')}",
        f"Test Type: {', '.join(candidate.get('test_type', []))}",
    ]

    duration = candidate.get("duration")
    if duration is not None:
        parts.append(f"Duration: {duration} minutes")

    return "\n".join(parts)

def rerank(query:str,candidates:list[dict], top_n:int=10 )->list[dict]:
    if not candidates:
        return []
    documents = [_format_candidate(c) for c in candidates] 
    response = co.rerank(
        model="rerank-english-v3.0",
        query=query,
        documents=documents,
        top_n=min(top_n, len(candidates)),
    )
    reranked = []
    for item in response.results:
        candidate = candidates[item.index]
        candidate = dict(candidate)
        candidate["rerank_score"] = item.relevance_score
        reranked.append(candidate)

    return reranked
