# generate_note_list.py（手動タグ分類対応済み）
import requests
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime
import re
from email.utils import parsedate_to_datetime

rss_url = "https://note.com/saiwaimoribuddhi/rss"
response = requests.get(rss_url)
root = ET.fromstring(response.content)

def categorize(title):
    if "神と仏のオープンカレッジ" in title:
        return "神と仏のオープンカレッジ"
    elif "仏教講座" in title:
        return "仏教講座"
    elif "幸いの森" in title:
        return "幸いの森"
    else:
        return "未分類"

def fetch_og_image(url):
    try:
        html = requests.get(url, timeout=5).text
        match = re.search(r'<meta property="og:image" content="([^"]+)"', html)
        return match.group(1) if match else "/img/no-image.jpg"
    except:
        return "/img/no-image.jpg"

def parse_date(pub_date):
    try:
        return parsedate_to_datetime(pub_date)
    except:
        return datetime.min

grouped_articles = defaultdict(list)

for item in root.findall("./channel/item"):
    title = item.findtext("title")
    link = item.findtext("link")
    pubDate = item.findtext("pubDate")
    description = item.findtext("description") or ""
    image_url = fetch_og_image(link)
    lead_text = re.sub(r'<[^>]+>', '', description).strip()
    lead_text = lead_text[:70] + "…" if len(lead_text) > 70 else lead_text

    date = pubDate[:16] if pubDate else "日付不明"
    category = categorize(title)
    grouped_articles[category].append({
        "title": title,
        "url": link,
        "date": date,
        "image": image_url,
        "lead": lead_text
    })

html_content = """<!DOCTYPE html>
<html lang=\"ja\">
<head>
  <meta charset=\"UTF-8\">
  <title>Note記事一覧</title>
  <style>
    body { font-family: sans-serif; padding: 1rem; line-height: 1.6; background: #fff; }
    h1 { color: #333; }
    h2 { color: #4caf50; margin-top: 1.5em; }
    li { margin-bottom: .5em; }
    a { text-decoration: none; color: #0066cc; }
    a:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <h1>Note記事 タグ別一覧</h1>
"""

for tag, articles in grouped_articles.items():
    html_content += f"<section>\n<h2>{tag}</h2>\n<ul>\n"
    for item in articles:
        html_content += f'<li><a href="{item["url"]}" target="_blank">{item["title"]}（{item["date"]}）</a></li>\n'
    html_content += "</ul>\n</section>\n"

html_content += """
</body>
</html>
"""

with open("note_list.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("✅ note_list.html を生成しました（カテゴリ分類あり）")

# === 追加：note_grid.html の生成 ===

articles = []
for item in root.findall("./channel/item"):
    title = item.findtext("title")
    link = item.findtext("link")
    pubDate = item.findtext("pubDate")
    description = item.findtext("description") or ""
    image_url = fetch_og_image(link)
    lead_text = re.sub(r'<[^>]+>', '', description).strip()
    lead_text = lead_text[:70] + "…" if len(lead_text) > 70 else lead_text

    date = parse_date(pubDate)
    articles.append({"title": title, "url": link, "date": date, "image": image_url, "lead": lead_text})

articles.sort(key=lambda x: x["date"], reverse=True)
latest_articles = articles[:6]

grid_html = """<!DOCTYPE html>
<html lang=\"ja\">
<head>
  <meta charset=\"UTF-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>Note 最新記事</title>
  <style>
    body { font-family: sans-serif; padding: 1rem; background: #fff; }
    h1 { color: #333; text-align: center; }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 1rem;
    }
    .card {
      border: 1px solid #ddd;
      padding: 1rem;
      border-radius: 5px;
      background: #f9f9f9;
      display: flex;
      flex-direction: column;
    }
    .card img {
      max-width: 100%;
      border-radius: 5px;
      margin-bottom: 0.5rem;
    }
    .card h3 {
      font-size: 1em;
      margin: 0 0 .3em;
    }
    .card p.date {
      font-size: .8em;
      color: #888;
      margin: 0.3em 0;
    }
    .card p.lead {
      font-size: .9em;
      color: #555;
    }
    a { color: #0066cc; text-decoration: none; }
    a:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <h1>最新記事</h1>
  <div class="grid">
"""

for item in latest_articles:
    grid_html += f"<div class='card'>\n"
    if item['image']:
        grid_html += f"  <img src='{item['image']}' alt='thumbnail'>\n"
    grid_html += f"  <h3><a href='{item['url']}' target='_blank'>{item['title']}</a></h3>\n"
    if item['date'] != datetime.min:
        grid_html += f"  <p class='date'>{item['date'].strftime('%Y年%m月%d日')}</p>\n"
    grid_html += f"  <p class='lead'>{item['lead']} <a href='{item['url']}' target='_blank'>続きを読む</a></p>\n"
    grid_html += "</div>\n"

grid_html += """
  </div>
</body>
</html>
"""

with open("note_grid.html", "w", encoding="utf-8") as f:
    f.write(grid_html)

print("✅ note_grid.html を生成しました（最新記事6件、画像・リード文対応）")
