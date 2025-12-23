from app.retrieval.qdrant_search import hybrid_search, sparse_search
from app.reranking.reranking_zerank import zerank_rerank
from app.services.intent_service import parse_intent
from app.services.selection_service import select_assessments, duration_ok
from app.services.intent_enrichment import enrich_with_llm


queries = [
    "Java developer",
    "Leadership and communication skills",
    "Cognitive ability test",
    "Short assessment under 30 minutes",
    "I am hiring for Java developers who can also collaborate effectively with my business teams. Looking for an assessment(s) that can be completed in 40 minutes."
]

def has_core_technical_signal(candidate, core_skills):
    text = f"{candidate.get('name','')} {candidate.get('description','')}".lower()
    return any(skill in text for skill in core_skills)


def run_pipeline(query:str,top_k:int=40,final_k:int=10):
    print("=" * 80)
    print("QUERY:")
    print(query)
    print()
    intent = parse_intent(query)
    print("INITIAL PARSED INTENT:")
    print(intent)
    intent = enrich_with_llm(intent,query)
    print("PARSED INTENT:")
    print(intent)
    print()

    candidates = hybrid_search(query,intent, top_k=top_k)
    if not candidates:
        candidates = sparse_search(query, intent, top_k=top_k)
    if intent.needs_technical and intent.core_technical_skills:
        pre_core_candidates = list(candidates)
        candidates = [c for c in candidates if has_core_technical_signal(c, intent.core_technical_skills)]
        if not candidates:
            candidates = pre_core_candidates

    if candidates:
        for c in candidates[:10]:
            name = c.get('name') or ''

    rerank_query = query
    if intent.core_technical_skills:
        rerank_query = (
            f"{query}\n\n"
            f"Core technical requirement: "
            f"{', '.join(intent.core_technical_skills)}"
        )

    candidates = zerank_rerank(rerank_query, candidates)

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
        """
KEY RESPONSIBITILES:

Manage the sound-scape of the station through appropriate creative and marketing interventions to Increase or Maintain the listenership
Acts as an interface between Programming & sales team, thereby supporting the sales team by providing creative inputs in order to increase the overall ad spends by clients
Build brand Mirchi by ideating fresh programming initiatives on air campaigns, programming led on-ground events & new properties to ensure brand differentiation & thus increase brand recall at station level
Invest time in local RJs to grow & develop them as local celebrities
Through strong networking, must focus on identifying the best of local talent and ensure to bring the creative minds from the market on board with Mirchi
Build radio as a category for both listeners & advertisers
People Management
Identifying the right talent and investing time in developing them by frequent feedback on their performance
Monitor, Coach and mentor team members on a regular basis
Development of Jocks as per guidelines
Must have an eye to spot the local talent to fill up vacancies locally




TECHNICAL SKILLS & QUALIFICATION REQUIRED:

Graduation / Post Graduation (Any specialisation) with 8 -12 years of relevant experience
Experience in digital content conceptualisation
Strong branding focus
Must be well-read in variety of areas and must keep up with the latest events in the city / cluster / country
Must know to read, write & speak English 


PERSONAL ATTRIBUTES:

Excellent communication skills
Good interpersonal skills
People management


Suggest me some tests for the above jd. The duration should be at most 90 mins
        """
    )
    run_pipeline(query)