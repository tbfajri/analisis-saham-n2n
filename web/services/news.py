import feedparser
from urllib.parse import quote

def google_news_rss(query: str, hl="id", gl="ID", ceid="ID:id", max_items=12):
    url = f"https://news.google.com/rss/search?q={quote(query)}&hl={hl}&gl={gl}&ceid={ceid}"
    feed = feedparser.parse(url)
    items = []
    for e in feed.entries[:max_items]:
        items.append({
            "title": e.get("title"),
            "link": e.get("link"),
            "published": e.get("published", ""),
            "source": getattr(e, "source", {}).get("title") if hasattr(e, "source") else ""
        })
    return items
