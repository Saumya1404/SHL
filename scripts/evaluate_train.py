import csv
import json
import time
from collections import defaultdict
from scripts.full_pipeline import run_pipeline
from urllib.parse import urlparse, unquote
import re

TRAIN_CSV = "data\\train_set.csv"
top_k = 50  
PREDICTIONS_OUT = "eval_predictions_50.csv"
METRICS_OUT = "eval_metrics_50.json"

def normalize_url(url: str) -> str:
    if not url:
        return ""
    url = str(url).strip()
    url = unquote(url)
    parsed = urlparse(url)
    path = parsed.path or ""
    if not path.startswith("/"):
        path = "/" + path
    path = re.sub(r"/+", "/", path)
    if path != "/":
        path = path.rstrip("/")
    return path.lower()


def _url_in_relevant(pred: str, relevant: set) -> bool:
    """Return True if pred matches any URL in relevant either exactly or by
    a conservative last-path-segment fallback.
    """
    if pred in relevant:
        return True
    try:
        pred_seg = pred.rstrip("/").split("/")[-1]
    except Exception:
        pred_seg = ""
    if not pred_seg:
        return False
    for r in relevant:
        r_seg = r.rstrip("/").split("/")[-1]
        if r_seg and r_seg == pred_seg:
            return True
    return False


def load_ground_truth(path):
    gt = defaultdict(set)
    with open(path, "r", encoding = "cp1252") as f:
        reader = csv.DictReader(f)
        for row in reader:
            query = row["Query"].strip()
            url = row["Assessment_url"].strip()
            gt[query].add(normalize_url(url))
        return gt
    
def recall_at_k(predicted, relevant,k):
    predicted = predicted[:k]
    return len(set(predicted) & relevant) / len(relevant)

def evaluate():
    ground_truth = load_ground_truth(TRAIN_CSV)
    recalls = []
    per_query_metrics = []
    predictions = []
    for query, relevant in ground_truth.items():
        results = run_pipeline(query, top_k=50, final_k=top_k)
        predicted_urls = [normalize_url(r.get("url") or "") for r in results]

        hits = set()
        for p in predicted_urls:
            if _url_in_relevant(p, relevant):
                hits.add(p)
        recall = len(hits) / len(relevant) if relevant else 0.0

        recalls.append(recall)

        print(f"Relevant URLs: {len(relevant)}")
        print(f"Hits@{top_k}: {len(hits)}")
        print(f"Recall@{top_k}: {recall:.3f}")

        per_query_metrics.append({
            "query": query,
            "relevant_count": len(relevant),
            "hits_at_10": len(hits),
            "recall_at_10": recall
        })

        for url in predicted_urls:
            predictions.append({
                "query": query,
                "predicted_url": url,
                "hit": _url_in_relevant(url, relevant)
            })
        
        time.sleep(30)


    mean_recall = sum(recalls) / len(recalls)
    with open(PREDICTIONS_OUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["query", "predicted_url", "hit"]
        )
        writer.writeheader()
        writer.writerows(predictions)
    metrics = {
        "mean_recall_at_10": mean_recall,
        "per_query": per_query_metrics
    }
    with open(METRICS_OUT, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"Mean Recall@{top_k}: {mean_recall:.3f}")

if __name__ == "__main__":
    evaluate()