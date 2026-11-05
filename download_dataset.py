import requests
import os
import time

URL = "https://hi.wikipedia.org/w/api.php"
OUTPUT_DIR = "dataset/documents"

os.makedirs(OUTPUT_DIR, exist_ok=True)

TARGET_DOCUMENTS = 100
downloaded = 0
seen_titles = set()

# Hindi Wikipedia categories to collect articles from
categories = [
    "भारत",
    "भारतीय इतिहास",
    "भारत के राज्य",
    "भारतीय संस्कृति",
    "भारतीय वैज्ञानिक",
    "विज्ञान",
    "गणित",
    "भौतिकी",
    "रसायन विज्ञान",
    "जीव विज्ञान",
    "प्रौद्योगिकी",
    "कंप्यूटर",
    "पर्यावरण",
    "भूगोल",
    "विश्व इतिहास"
]

session = requests.Session()

session.headers.update({
    "User-Agent": "HindiPositionalIndexer/1.0 (educational project)"
})


def get_category_articles(category):
    """Fetch article titles from a Hindi Wikipedia category."""

    params = {
        "action": "query",
        "format": "json",
        "list": "categorymembers",
        "cmtitle": "श्रेणी:" + category,
        "cmlimit": 100,
        "cmtype": "page"
    }

    titles = []

    while True:
        response = session.get(URL, params=params, timeout=30)
        response.raise_for_status()

        result = response.json()

        members = result.get("query", {}).get("categorymembers", [])

        for member in members:
            title = member["title"]

            if title not in seen_titles:
                titles.append(title)
                seen_titles.add(title)

        if "continue" not in result:
            break

        params.update(result["continue"])

    return titles


def download_article(title):
    """Download plain text of one Wikipedia article."""

    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "titles": title,
        "explaintext": 1,
        "redirects": 1
    }

    response = session.get(URL, params=params, timeout=30)
    response.raise_for_status()

    pages = response.json().get("query", {}).get("pages", {})

    for page in pages.values():

        if page.get("missing") is not None:
            return None, None

        content = page.get("extract", "").strip()
        actual_title = page.get("title", title)

        if len(content) < 100:
            return None, None

        return actual_title, content

    return None, None


# Collect article titles
all_titles = []

print("Collecting Hindi Wikipedia articles...")

for category in categories:
    try:
        titles = get_category_articles(category)
        all_titles.extend(titles)
        print(category, "->", len(titles), "articles")

    except requests.RequestException as error:
        print("Category error:", category, error)

# Download 100 unique articles
print("\nDownloading articles...\n")

for title in all_titles:

    if downloaded >= TARGET_DOCUMENTS:
        break

    try:
        actual_title, content = download_article(title)

        if not content:
            continue

        downloaded += 1

        filename = f"DOC{downloaded}.txt"
        filepath = os.path.join(OUTPUT_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as file:
            file.write(actual_title + "\n")
            file.write(content)

        print(f"{downloaded}/100 Downloaded: {actual_title}")

        time.sleep(0.3)

    except requests.RequestException as error:
        print("Download error:", title, error)
        time.sleep(1)

print("\n========== DATASET SUMMARY ==========")
print("Total documents downloaded:", downloaded)
print("Output folder:", OUTPUT_DIR)

if downloaded == TARGET_DOCUMENTS:
    print("SUCCESS: 100 documents downloaded!")
else:
    print("Only", downloaded, "documents downloaded.")
    print("Run the script again or add more categories.")