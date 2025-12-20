from retrieval.qdrant_search import hybrid_search
from reranking.cohere_reranking import rerank
from app.services.intent_service import parse_intent
from app.services.selection_service import select_assessments
queries = [
    "Java developer",
    "Leadership and communication skills",
    "Cognitive ability test",
    "Short assessment under 30 minutes",
    "I am hiring for Java developers who can also collaborate effectively with my business teams. Looking for an assessment(s) that can be completed in 40 minutes."
]

def run_pipeline(query:str,top_k:int=40,final_k:int=10):
    print("=" * 80)
    print("QUERY:")
    print(query)
    print()
    intent = parse_intent(query)
    print("PARSED INTENT:")
    print(intent)
    print()

    candidates = hybrid_search(query, top_k=top_k)
    candidates = rerank(query, candidates)
    for c in candidates[:5]:
        print(
            f"- {c['name']} | {c['test_type']} | "
            f"{c['duration']} min | score={c.get('rerank_score', 0):.3f}"
        )

    final = select_assessments(
        candidates=candidates,
        intent=intent,
        k=final_k
    )
    print("FINAL RECOMMENDATIONS:")
    for i, c in enumerate(final, 1):
        print(
            f"{i}. {c['name']} | {c['test_type']} | "
            f"{c['duration']} min\n   {c['url']}"
        )

    return final
if __name__ == "__main__":
    query = (
        "I am hiring for Java developers who can also collaborate effectively "
        "with my business teams. Looking for an assessment(s) that can be "
        "completed in 40 minutes."
    )
    run_pipeline(query)