from retrieval.qdrant_search import hybrid_search
from reranking.cohere_reranking import rerank

queries = [
    "Java developer",
    "Leadership and communication skills",
    "Cognitive ability test",
    "Short assessment under 30 minutes",
    "I am hiring for Java developers who can also collaborate effectively with my business teams. Looking for an assessment(s) that can be completed in 40 minutes."
]

for query in queries:
    print("=" * 80)
    print(f"QUERY: {query}\n")

    retrieved = hybrid_search(query, top_k=40)

    print("Top 5 retrieved (before rerank):")
    for r in retrieved[:5]:
        print(f"- {r['name']} | {r['test_type']} | {r['duration']} min")

    reranked = rerank(query, retrieved, top_n=10)

    print("\nTop 10 after rerank:")
    for r in reranked:
        print(
            f"- {r['name']} | {r['test_type']} | "
            f"{r['duration']} min | score={r['rerank_score']:.3f}"
        )
