from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from scripts.full_pipeline import run_pipeline

app = FastAPI(title="SHL Recommender API")


class RecommendRequest(BaseModel):
    query: str
    top_k: Optional[int] = 50
    final_k: Optional[int] = 10


class Assessment(BaseModel):
    url: str
    name: Optional[str] = None
    adaptive_support: Optional[str] = "No"
    description: Optional[str] = None
    duration: Optional[int] = None
    remote_support: Optional[str] = "No"
    test_type: Optional[List[str]] = None


class ResponseWrapper(BaseModel):
    recommended_assessments: List[Assessment]


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/recommend", response_model=ResponseWrapper)
def recommend(req: RecommendRequest):
    if not req.query:
        raise HTTPException(status_code=400, detail="query is required")
    
    results = run_pipeline(req.query, top_k=req.top_k, final_k=req.final_k)

    out = []
    for c in results:
        adaptive_val = c.get("adaptive_testing") or c.get("adaptive_support") or "No"
        remote_val = c.get("remote_testing") or c.get("remote_support") or "No"

        out.append({
            "url": c.get("url"),
            "name": c.get("name"),
            "adaptive_support": adaptive_val,
            "description": c.get("description"),
            "duration": c.get("duration") or c.get("assessment_duration"),
            "remote_support": remote_val,
            "test_type": c.get("test_type")
        })

    return {"recommended_assessments": out}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)