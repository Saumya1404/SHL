# SHL Assessment Recommendation System

An intelligent assessment recommendation system that retrieves, ranks, and balances SHL **Individual Test Solutions** based on hiring queries, job descriptions, or JD text.  
The system combines **intent extraction, hybrid retrieval, LLM-based enrichment, reranking, and rule-based selection** to optimize relevance and Recall@K.

---

## Live Links

- **Frontend (Streamlit UI):**  
  https://shl-saumya.streamlit.app/

- **Backend API (FastAPI):**  
  https://shl-5osm.onrender.com

---

## Problem Overview

Hiring managers often rely on keyword-based search to identify suitable assessments, which fails to capture:
- Role intent and seniority
- Balance between technical and behavioral skills
- Time and duration constraints
- Semantic relevance beyond keywords

This system addresses these limitations by understanding hiring intent from natural language queries and returning a balanced, ranked list of relevant SHL assessments.

---

## System Architecture

```
Query / JD
   ↓
Intent Parsing (rules + regex)
   ↓
LLM-based Intent Enrichment
   ↓
Hybrid Retrieval (Dense + Sparse, RRF)
   ↓
Re-ranking (ZeroEntropy)
   ↓
Rule-based Selection & Balancing
   ↓
Final Recommendations
```

---

## Key Features

- **Multiple Input Modes**
  - Natural language query
  - Job description text
  - Batch CSV prediction support

- **Hybrid Retrieval**
  - Dense embeddings using `sentence-transformers/all-MiniLM-L6-v2`
  - Sparse retrieval using BM25 (Qdrant)
  - Reciprocal Rank Fusion (RRF) for combining results

- **Intent-Aware Ranking**
  - Duration constraints
  - Core vs supporting technical skills
  - Behavioral vs technical balance
  - Seniority and role awareness

- **LLM-Guided Enrichment**
  - Skill classification and prioritization
  - Filtering of generic role terms to avoid ranking noise

- **Diversity & Redundancy Control**
  - Penalizes overlapping test types
  - Penalizes near-duplicate assessment names
  - Encourages coverage across domains

---

## API Overview

### Health Check

```
GET /health
```

Response:
```json
{ "status": "healthy" }
```

---

### Recommendation Endpoint

```
POST /recommend
```

Request body:
```json
{
  "query": "I am hiring for a senior Java developer who can collaborate with stakeholders",
  "top_k": 50,
  "final_k": 10
}
```

Response:
```json
{
  "recommended_assessments": [
    {
      "url": "https://www.shl.com/...",
      "name": "Assessment Name",
      "description": "Assessment description",
      "duration": 40,
      "test_type": ["K"],
      "adaptive_testing": "No",
      "remote_testing": "Yes"
    }
  ]
}
```

---

## Frontend (Streamlit)

The Streamlit UI provides:
- Text input for hiring queries
- Sliders for retrieval depth and final result count
- Interactive display of recommended assessments

Live UI:  
https://shl-saumya.streamlit.app/

---

## Evaluation

- **Primary Metric:** Mean Recall@K
- **Default K:** 10
- **Evaluation Dataset:** Human-labeled training queries
- **Outputs:**
  - Per-query prediction CSVs
  - Mean Recall@K metrics (JSON)

Evaluation scripts are available under:
```
scripts/evaluate_train.py
```

---

## Data Pipeline

- **Web Scraping**
  - SHL product catalog scraped using BeautifulSoup
  - Pre-packaged job solutions excluded
  - Approximately 377 individual test solutions retained

- **Storage & Indexing**
  - Cleaned catalog stored as JSON
  - Embedded and indexed in Qdrant (cloud-hosted)

---

## Configuration & Environment

Required environment variables:
```
QDRANT_URL
QDRANT_API_KEY
ZEROENTROPY_API_KEY
GOOGLE_GENAI_API_KEY
```

Optional (fallback reranker):
```
COHERE_API_KEY
```

---

## Tech Stack

- Backend: FastAPI, Uvicorn
- Frontend: Streamlit
- Vector Database: Qdrant (cloud)
- Embeddings: Sentence Transformers (MiniLM)
- LLM: Google GenAI (Gemma)
- Reranking: ZeroEntropy (ZeRank)
- Web Scraping: BeautifulSoup

---

## Repository Structure (High-Level)

```
app/
 ├── main.py
 ├── retrieval/
 ├── services/
 ├── reranking/
 ├── core/
 └── streamlit_app.py

scripts/
 ├── get_all_data.py
 ├── upload_to_qdrant.py
 ├── generate_predictions.py
 └── evaluate_train.py

data/
 ├── catalog_cleaned.json
 ├── train_set.csv
 └── test_set.csv
```

---

## Notes

- All recommendations are generated strictly from the scraped SHL product catalog
- No hardcoded assessment mappings
- Designed to be modular, testable, and extensible
