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
    adaptive_support: Optional[bool] = False
    description: Optional[str] = None
    duration: Optional[int] = None
    remote_support: Optional[bool] = False
    test_type: Optional[List[str]] = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/recommend", response_model=List[Assessment])
def recommend(req: RecommendRequest):
    if not req.query:
        raise HTTPException(status_code=400, detail="query is required")

    # Run the pipeline (this may call external services and take time)
    results = run_pipeline(req.query, top_k=req.top_k, final_k=req.final_k)

    out = []
    for c in results:
        out.append({
            "url": c.get("url"),
            "name": c.get("name"),
            "adaptive_support": c.get("adaptive_support", False),
            "description": c.get("description"),
            # prefer canonical numeric duration if present
            "duration": c.get("duration") or c.get("assessment_duration"),
            "remote_support": c.get("remote_support", c.get("remote_testing", False)),
            "test_type": c.get("test_type")
        })

    return out


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)