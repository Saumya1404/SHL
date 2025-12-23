from app.retrieval.qdrant_search import hybrid_search

queries = [
    "Java developer",
    "Leadership and communication skills",
    "Cognitive ability test",
    "Short assessment under 30 minutes",
    "I am hiring for Java developers who can also collaborate effectively with my business teams. Looking for an assessment(s) that can be completed in 40 minutes."
]

for q in queries:
    print(f"\nQuery: {q}")
    results = hybrid_search(q, top_k=10)
    for r in results:
        print(f"- {r['name']} | {r['test_type']} | {r['duration']} min")
