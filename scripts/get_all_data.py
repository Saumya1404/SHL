import requests
from bs4 import BeautifulSoup
import time
import os
import csv
import random
import json


INPUT_FILE = "data/assessment_urls.txt"
OUTPUT_FILE = "data/data/catalog.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate", 
    "Connection": "keep-alive",
    "Referer": "https://www.shl.com/",
}

def normalize_key(text: str) -> str:
    return (
        text.strip()
        .lower()
        .replace("&", "and")
        .replace(" ", "_")
    )


def extract_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    data = {}
    h1 = soup.find("h1")
    if h1:
        data["name"] = h1.get_text(strip=True)

    rows = soup.find_all(
        "div",
        class_="product-catalogue-training-calendar__row"
    )

    for row in rows:
        h4 = row.find("h4")
        if not h4:
            continue

        key = normalize_key(h4.get_text())
        primary_p = row.find("p", recursive=False)
        if primary_p and key not in data:
            data[key] = primary_p.get_text(strip=True)
    for row in rows:
        flex_div = row.find("div", class_="d-flex")
        if not flex_div:
            continue       
        for p in flex_div.find_all("p"):
            text = p.get_text(strip=True)
            if "Test Type" in text:
                type_spans = p.find_all("span", class_="product-catalogue__key")
                if type_spans:
                    data["test_type"] = [s.get_text(strip=True) for s in type_spans]

            elif "Remote Testing" in text:
                if p.find("span", class_="ms-2 || catalogue__circle -yes"):
                    data["remote_testing"] = "Yes"
                else:
                    data["remote_testing"] = "No"

    return data

def fetch_page(session, url):
    response = session.get(url, timeout=60)
    response.raise_for_status()
    return response.text


def main():
    try:
        with open(INPUT_FILE,"r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip()]
        print(f"Found {len(urls)} URLs to process.")
    except FileNotFoundError:
        print(f"Input file '{INPUT_FILE}' not found.")
        return
    
    session = requests.Session()
    session.headers.update(HEADERS)

    catalog = []
    failed_urls = []
    for idx,url in enumerate(urls, start=1):
        print(f"Processing {idx}/{len(urls)}: {url}")
        try:
            html = fetch_page(session,url)  
            if html is None:
                failed_urls.append(url)
                continue

            data = extract_data(html)
            data["url"] = url 
            catalog.append(data)

            time.sleep(random.uniform(1.0, 2.0))

        except Exception as e:
            print(f"[ERROR] Failed for {url}: {e}")
            failed_urls.append(url)

    os.makedirs("data", exist_ok=True)
    with open("data/catalog.json", "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)


    with open("data/failed_urls.txt", "w", encoding="utf-8") as f:
        for u in failed_urls:
            f.write(u + "\n")

    print(f"Saved {len(catalog)} assessments")
    print(f"Failed URLs: {len(failed_urls)}")

if __name__ == "__main__":
    main()