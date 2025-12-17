from bs4 import BeautifulSoup
import requests
import time

url = "https://www.shl.com/products/product-catalog/view/adobe-photoshop-cc/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Referer": "https://www.shl.com/",
}

def fetch_page(url):
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    time.sleep(1.5)
    return response.text

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

    # Assessment name
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

        # Primary value: first direct <p>
        primary_p = row.find("p", recursive=False)
        if primary_p:
            data[key] = primary_p.get_text(strip=True)

        # Secondary attributes inside d-flex
        flex_div = row.find("div", class_="d-flex")
        if not flex_div:
            continue

        for p in flex_div.find_all("p"):
            text = p.get_text(strip=True)

            # ---- Test Type ----
            if "Test Type" in text:
                type_spans = p.find_all("span", class_="product-catalogue__key")
                if type_spans:
                    data["test_type"] = [s.get_text(strip=True) for s in type_spans]

            # ---- Remote Testing ----
            elif "Remote Testing" in text:
                if p.find("span", class_="ms-2 || catalogue__circle -yes"):
                    data["remote_testing"] = "Yes"
                else:
                    data["remote_testing"] = "No"

    return data


if __name__ == "__main__":
    try:
        html = fetch_page(url)
        data = extract_data(html)
        print(data)
    except requests.exceptions.HTTPError as e:
        print(f"Failed to fetch page: {e}")
