import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from email.utils import format_datetime
from xml.sax.saxutils import escape

URL = "https://www.equitybulls.com/generic.php?cat=4"

headers = {
    "User-Agent": "Mozilla/5.0 (compatible; EquityBullsRSS/1.0)"
}

response = requests.get(URL, headers=headers, timeout=30)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

items = []
seen = set()

# Find article links on the Stock Report page
for a in soup.find_all("a", href=True):
    title = a.get_text(" ", strip=True)
    href = a["href"].strip()

    if not title or len(title) < 10:
        continue

    if href.startswith("/"):
        href = "https://www.equitybulls.com" + href
    elif href.startswith("http://"):
        href = href.replace("http://", "https://", 1)

    if "equitybulls.com" not in href:
        continue

    # Avoid navigation/category links
    if "generic.php" in href or "keywords.php" in href:
        continue

    if title in seen:
        continue

    seen.add(title)

    items.append({
        "title": title,
        "link": href
    })

    if len(items) >= 30:
        break

now = datetime.now(timezone.utc)

xml = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<rss version="2.0">',
    '<channel>',
    '<title>EquityBulls Stock News</title>',
    '<link>https://www.equitybulls.com/generic.php?cat=4</link>',
    '<description>Latest EquityBulls Stock Report news</description>',
    '<language>en-IN</language>',
    f'<lastBuildDate>{format_datetime(now)}</lastBuildDate>'
]

for item in items:
    xml.append("<item>")
    xml.append(f"<title>{escape(item['title'])}</title>")
    xml.append(f"<link>{escape(item['link'])}</link>")
    xml.append(f"<guid isPermaLink=\"true\">{escape(item['link'])}</guid>")
    xml.append(f"<pubDate>{format_datetime(now)}</pubDate>")
    xml.append("<description>EquityBulls Stock Report</description>")
    xml.append("</item>")

xml.extend([
    "</channel>",
    "</rss>"
])

with open("feed.xml", "w", encoding="utf-8") as f:
    f.write("\n".join(xml))

print(f"Generated RSS feed with {len(items)} articles.")
