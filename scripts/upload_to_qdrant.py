import json
import os
from typing import List
from qdrant_client import QdrantClient,models
from qdrant_client.models import PointStruct, SparseVector
from fastembed import TextEmbedding, SparseTextEmbedding
from dotenv import load_dotenv
load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "shl_assessments"

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)

print(f"Collection Created: {COLLECTION_NAME}")
client.recreate_collection(
    collection_name = COLLECTION_NAME,
    vectors_config = {
        "dense": models.VectorParams(
            size=384,
            distance = models.Distance.COSINE
        )
    },
    sparse_vectors_config={
        "sparse":models.SparseVectorParams(
            index=models.SparseIndexParams(
                on_disk=False
            )
        )
    }
)



with open("data/catalog_cleaned.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Loaded {len(data)} records from catalog_cleaned.json")

dense_model = TextEmbedding("sentence-transformers/all-MiniLM-L6-v2")
sparse_model = SparseTextEmbedding("Qdrant/bm25")

documents :List[str] = []
for item in data:
    name = item.get("name", "")
    level = item.get("job_levels","")
    t_type = ", ".join(item.get("test_type",[]))
    desc = item.get("description","")

    search_text = f"Title: {name}. Job Levels: {level}. Test Types: {t_type}. Description: {desc}"
    documents.append(search_text)

print("Generating embeddings...")
dense_embeddings = list(dense_model.embed(documents))
sparse_embeddings = list(sparse_model.embed(documents))

points = []

for idx,item in enumerate(data):
    dense_vec = dense_embeddings[idx]
    sparse_vec = sparse_embeddings[idx]
    payload = {
        "name": item.get("name"),
        "url": item.get("url"),
        "description": item.get("description"),
        "assessment_duration": item.get("assessment_duration",0),
        "test_type": item.get("test_type",[]),
        "job_levels": item.get("job_levels",""),
        "remote_testing": item.get("remote_testing","Yes")
    }
    points.append(PointStruct(
        id=idx,
        vector = {
            "dense": dense_vec,
            "sparse": SparseVector(
                indices = sparse_vec.indices.tolist(),
                values = sparse_vec.values.tolist()
            )
        },
        payload = payload
    ))

client.upload_points(
    collection_name=COLLECTION_NAME,
    points=points,
    batch_size=64
)

print("Uploaded")