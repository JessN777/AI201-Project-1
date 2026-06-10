import requests
from bs4 import BeautifulSoup
import os
import time
import re
import xml.etree.ElementTree as ET

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}

RSS_FEEDS = [
    "https://news.google.com/rss/search?q=FIFA+Club+World+Cup&hl=en-US&gl=US&ceid=US:en&tbs=qdr:m",
    "https://news.google.com/rss/search?q=Club+World+Cup+2026&hl=en-US&gl=US&ceid=US:en&tbs=qdr:m",
    "https://news.google.com/rss/search?q=Club+World+Cup+soccer+news&hl=en-US&gl=US&ceid=US:en&tbs=qdr:m",
    "https://news.google.com/rss/search?q=Club+World+Cup+Real+Madrid&hl=en-US&gl=US&ceid=US:en&tbs=qdr:m",
    "https://news.google.com/rss/search?q=Club+World+Cup+Manchester+City&hl=en-US&gl=US&ceid=US:en&tbs=qdr:m",
    "https://news.google.com/rss/search?q=Club+World+Cup+Bayern+Munich&hl=en-US&gl=US&ceid=US:en&tbs=qdr:m",
    "https://news.google.com/rss/search?q=Club+World+Cup+Chelsea&hl=en-US&gl=US&ceid=US:en&tbs=qdr:m",
    "https://news.google.com/rss/search?q=Club+World+Cup+Messi+Inter+Miami&hl=en-US&gl=US&ceid=US:en&tbs=qdr:m",
    "https://news.google.com/rss/search?q=Club+World+Cup+Mbappe&hl=en-US&gl=US&ceid=US:en&tbs=qdr:m",
    "https://news.google.com/rss/search?q=Club+World+Cup+Haaland&hl=en-US&gl=US&ceid=US:en&tbs=qdr:m",
    "https://news.google.com/rss/search?q=Club+World+Cup+results+scores&hl=en-US&gl=US&ceid=US:en&tbs=qdr:m",
    "https://news.google.com/rss/search?q=Club+World+Cup+final+winner&hl=en-US&gl=US&ceid=US:en&tbs=qdr:m",
]

def clean_filename(title):
    title = re.sub(r'[\\/*?:"<>|]', "", title)
    return title[:80].strip() + ".txt"

def fetch_rss_articles(feed_url):
    response = requests.get(feed_url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    root = ET.fromstring(response.content)
    articles = []
    for item in root.findall(".//item"):
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        description = item.findtext("description", "").strip()
        description = BeautifulSoup(description, "html.parser").get_text()
        if title and link:
            articles.append({"title": title, "link": link, "description": description})
    return articles

def fetch_article_text(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
            tag.decompose()
        for selector in ["article", "main", "[class*='article']", "[class*='content']", "[class*='story']"]:
            content = soup.select_one(selector)
            if content:
                text = content.get_text(separator="\n", strip=True)
                if len(text) > 200:
                    return text[:4000]
        paragraphs = soup.find_all("p")
        text = "\n".join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 40)
        return text[:4000] if len(text) > 200 else ""
    except Exception:
        return ""

def save_article(title, description, body, output_dir="."):
    filename = clean_filename(title)
    filepath = os.path.join(output_dir, filename)
    if os.path.exists(filepath):
        return False
    content = f"{title}\n\n"
    if description:
        content += f"{description}\n\n"
    if body:
        content += body
    if len(content.strip()) < 100:
        return False
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Saved: {filename[:70]}")
    return True

def scrape(output_dir=".", max_articles=100):
    seen_titles = set()
    # Also skip titles of files already saved
    for f in os.listdir(output_dir):
        if f.endswith(".txt"):
            seen_titles.add(f[:-4])  # filename without .txt

    saved = 0
    for feed_url in RSS_FEEDS:
        if saved >= max_articles:
            break
        print(f"\nFetching: {feed_url[50:90]}...")
        try:
            articles = fetch_rss_articles(feed_url)
            print(f"  Found {len(articles)} articles")
        except Exception as e:
            print(f"  Error: {e}")
            continue

        for article in articles:
            if saved >= max_articles:
                break
            title = article["title"]
            if title in seen_titles:
                continue
            seen_titles.add(title)

            print(f"  Fetching: {title[:60]}...")
            body = fetch_article_text(article["link"])
            if save_article(title, article["description"], body, output_dir):
                saved += 1
            time.sleep(1.5)

    print(f"\nDone — saved {saved} articles total in '{output_dir}'")
    return saved

if __name__ == "__main__":
    scrape(output_dir=".", max_articles=100)
