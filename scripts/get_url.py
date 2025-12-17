import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List
import time

BASE_URL = "https://www.shl.com"
CATALOG_URL = "https://www.shl.com/products/product-catalog/?start=12&type=1&type=1"


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Referer": "https://www.shl.com/",
}


def fetch_catalog_page(url):
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    time.sleep(1.5)  
    return response.text


def extract_individual_test_urls(html: str) -> List[str]:
    soup = BeautifulSoup(html, "html.parser")

    entity_rows = soup.find_all("tr", attrs={"data-entity-id": True})

    # IMPORTANT: empty list means "end of pagination", not an error
    if not entity_rows:
        return []

    assessment_urls = []

    for row in entity_rows:
        link = row.find("a", href=True)
        if not link:
            continue

        href = link["href"].strip()
        full_url = urljoin(BASE_URL, href)
        assessment_urls.append(full_url)

    # Deduplicate while preserving order
    seen = set()
    unique_urls = []
    for url in assessment_urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)

    return unique_urls

if __name__ == "__main__":
    start = 0
    all_urls = set()

    while True:
        print(f"Fetching catalog page with start={start}")

        url = f"https://www.shl.com/products/product-catalog/?start={start}&type=1&type=1"
        html = fetch_catalog_page(url)
        urls = extract_individual_test_urls(html)

        if not urls:
            print("No more URLs found, ending pagination.")
            break

        new_urls = set(urls) - all_urls
        if not new_urls:
            print("No new URLs found, ending pagination.")
            break

        all_urls.update(new_urls)
        start += 12

    output_path = "data/assessment_urls.txt"
    with open(output_path, "w+", encoding="utf-8") as f:
        for u in sorted(all_urls):
            f.write(u + "\n")

    print(f"Saved {len(all_urls)} unique assessment URLs to {output_path}")
