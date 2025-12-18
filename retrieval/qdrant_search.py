from qdrant_client import QdrantClient
from qdrant_client.models import SparseVector,NamedVector,Prefetch,RrfQuery
from fastembed import TextEmbedding,SparseTextEmbedding
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

dense_model = TextEmbedding("sentence-transformers/all-MiniLM-L6-v2")
sparse_model = SparseTextEmbedding("Qdrant/bm25")


def hybrid_search(query:str, top_k:int=50):
    dense_vector = next(dense_model.embed([query]))
    sparse_embedding = next(sparse_model.embed([query]))

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
            "description": payload.get("description")
        })
    return candidates