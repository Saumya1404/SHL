from qdrant_client import QdrantClient
from qdrant_client.models import SparseVector,NamedVector,Prefetch,RrfQuery, Filter, FieldCondition, Range,MatchValue
from fastembed import TextEmbedding,SparseTextEmbedding
from app.services.intent_service import Intent
from dotenv import load_dotenv
import os
load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "shl_assessments"
client = QdrantClient(
    url = QDRANT_URL,
    api_key= QDRANT_API_KEY
)

KEYWORD_CLASS_WEIGHTS = {
    "critical": 1.0,
    "context": 1.3,
    "default": 1.0,
}


dense_model = TextEmbedding("sentence-transformers/all-MiniLM-L6-v2")
sparse_model = SparseTextEmbedding("Qdrant/bm25")

KEYWORD_CLASS_WEIGHTS = {
    "critical": 2.0,
    "context": 1.3,
    "default": 1.0,
}
def build_sparse_query(intent: Intent) -> str:
    terms = []

    for skill in intent.core_technical_skills:
        importance = intent.keyword_importance.get(skill, "critical")
        repeat = {"critical": 8, "context": 6, "default": 5}[importance]
        terms.extend([skill] * repeat)
    for skill in intent.technical_skills:
        importance = intent.keyword_importance.get(skill, "context")
        repeat = {"critical": 4, "context": 3, "default": 2}[importance]
        terms.extend([skill] * repeat)

    for skill in intent.behavioral_skills:
        importance = intent.keyword_importance.get(skill, "default")
        repeat = {"critical": 2, "context": 1, "default": 1}[importance]
        terms.extend([skill] * repeat)
    
    return " ".join(terms)

def build_qdrant_filter_from_intent(intent:Intent):
    must = []
    should = []
    if intent.max_duration_minutes is not None:
        must.append(
            FieldCondition(key = "assessment_duration",
                           range = Range(lte=int(intent.max_duration_minutes)))
        )
    if getattr(intent,"role_type",None):
        must.append(
            FieldCondition(key="role_type",
                           match=MatchValue(value=intent.role_type))
        )
    if getattr(intent,"seniority",None):
        must.append(
            FieldCondition(key="seniority",
                           match=MatchValue(value=intent.seniority)
        ))
    
    if intent.needs_technical:
        tech_types = ["Knowledge & Skills", "Ability & Aptitude"]
        for t in tech_types:
            should.append(
                FieldCondition(
                    key="test_type",
                    match=MatchValue(value=t)
                )
            )
    
    kw_imp = intent.keyword_importance or {}
    if kw_imp:
        for kw, cls in kw_imp.items():
            if cls == "critical":
                should.append(
                    FieldCondition(
                        key="test_type",
                        match=MatchValue(value=kw)
                    )
                )

    if not must and not should:
        return None
    return Filter(must= must or None , should= should or None)

        
def hybrid_search(query:str,intent:Intent, top_k:int=50):
    dense_vector = next(dense_model.embed([query]))

    sparse_query = build_sparse_query(intent)
    if not sparse_query:
        sparse_query = query
    sparse_embedding = next(sparse_model.embed([sparse_query]))
    sparse_vector = SparseVector(
        indices = sparse_embedding.indices,
        values = sparse_embedding.values
    )   
    response = client.query_points(
        collection_name=COLLECTION_NAME,
        prefetch=[
            Prefetch(
                using="dense",
                query=dense_vector,
                limit=top_k,
            ),
            Prefetch(
                using="sparse",
                query=sparse_vector,
                limit=top_k,
            ),
        ],
        query=RrfQuery(rrf={"k": 60}),
        limit=top_k,
        with_payload=True,
    )

    




    candidates = []
    for point in response.points:
        payload = point.payload or {}
        candidates.append({
            "id": point.id,
            "score": point.score,
            "name": payload.get("name"),
            "test_type": payload.get("test_type"),
            "duration": payload.get("assessment_duration"),
            "url": payload.get("url"),
            "description": payload.get("description"),
            "remote_testing": payload.get("remote_testing"),
            "adaptive_testing": payload.get("adaptive_testing")
        })
    return candidates


def sparse_search(query: str, intent: Intent, top_k: int = 50):
    sparse_query = build_sparse_query(intent)
    if not sparse_query:
        sparse_query = query
    sparse_embedding = next(sparse_model.embed([sparse_query]))
    sparse_vector = SparseVector(
        indices=sparse_embedding.indices,
        values=sparse_embedding.values,
    )

    response = client.query_points(
        collection_name=COLLECTION_NAME,
        prefetch=[
            Prefetch(
                using="sparse",
                query=sparse_vector,
                limit=top_k,
            ),
        ],
        query=RrfQuery(rrf={"k": 60}),
        limit=top_k,
        with_payload=True,
    )
    

    candidates = []
    for point in response.points:
        payload = point.payload or {}
        candidates.append({
            "id": point.id,
            "score": point.score,
            "name": payload.get("name"),
            "test_type": payload.get("test_type"),
            "duration": payload.get("assessment_duration"),
            "url": payload.get("url"),
            "description": payload.get("description"),
            "remote_testing": payload.get("remote_testing"),
            "adaptive_testing": payload.get("adaptive_testing")
        })
    return candidates