import requests
import os
import time
import re

HEADERS = {"User-Agent": "worldcup-rag-scraper/1.0"}

SEARCHES = [
    ("soccer", "club world cup"),
    ("soccer", "FIFA club world cup 2025"),
    ("soccer", "CWC 2025"),
    ("soccer", "club world cup mbappe"),
    ("soccer", "club world cup haaland"),
]

def clean_filename(title):
    title = re.sub(r'[\\/*?:"<>|]', "", title)
    return title[:80].strip() + ".txt"

def fetch_posts(subreddit, query="", limit=15):
    if query:
        url = f"https://www.reddit.com/r/{subreddit}/search.json"
        params = {"q": query, "sort": "top", "t": "year", "limit": limit, "restrict_sr": 1}
    else:
        url = f"https://www.reddit.com/r/{subreddit}/top.json"
        params = {"t": "year", "limit": limit}

    response = requests.get(url, headers=HEADERS, params=params, timeout=10)
    response.raise_for_status()
    posts = response.json()["data"]["children"]
    print(f"  Fetched {len(posts)} posts from r/{subreddit} '{query}'")
    return posts

def fetch_top_comments(post_id, subreddit, limit=5):
    url = f"https://www.reddit.com/r/{subreddit}/comments/{post_id}.json"
    params = {"limit": limit, "depth": 1}
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()
        comments_data = response.json()[1]["data"]["children"]
        comments = []
        for c in comments_data:
            body = c["data"].get("body", "").strip()
            if body and body not in ("[removed]", "[deleted]") and len(body) > 20:
                comments.append(body)
        return comments
    except Exception:
        return []

def save_post(post_data, output_dir="."):
    title = post_data["title"]
    body = post_data.get("selftext", "").strip()
    post_id = post_data["id"]
    subreddit = post_data["subreddit"]
    score = post_data.get("score", 0)

    # Skip removed/deleted posts and low-quality ones
    if body in ("[removed]", "[deleted]"):
        body = ""

    filename = clean_filename(title)
    filepath = os.path.join(output_dir, filename)

    if os.path.exists(filepath):
        return False

    # Fetch top comments to add context even if post has no body
    comments = fetch_top_comments(post_id, subreddit, limit=5)
    time.sleep(1)

    # Build file content
    content = f"{title}\n(Score: {score} | r/{subreddit})\n\n"
    if body:
        content += f"{body}\n\n"
    if comments:
        content += "Top comments:\n"
        for c in comments:
            content += f"- {c}\n"

    # Only save if there's meaningful content beyond just the title
    if not body and not comments:
        print(f"  Skipped (no content): {title[:60]}")
        return False

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"  Saved: {filename[:60]}")
    return True

def scrape(output_dir=".", limit=15):
    saved = 0
    for subreddit, query in SEARCHES:
        try:
            posts = fetch_posts(subreddit, query, limit=limit)
            for post in posts:
                if save_post(post["data"], output_dir):
                    saved += 1
            time.sleep(2)
        except Exception as e:
            print(f"Error fetching r/{subreddit} '{query}': {e}")

    print(f"\nDone — saved {saved} new posts.")
    if saved > 0:
        print("Run python query.py to embed them and start the app.")

if __name__ == "__main__":
    scrape(output_dir=".", limit=15)
