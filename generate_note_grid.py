# generate_note_grid.py
# ── NOTEのRSSから最新6件を取得して、サムネイル＋リード文カード形式のHTMLを生成

import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import re

rss_url = "https://note.com/saiwaimoribuddhi/rss"
response = requests.get(rss_url)
root = ET.fromstring(response.content)

items = root.findall("./channel/item")[:6]  # 最新6件に限定

articles = []

for item in items:
    title = item.findtext("title")
    link = item.findtext("link")
    pubDate = item.findtext("pubDate")
    description_raw = item.findtext("description")

    # サムネイル取得（<img src="..."> の最初のURL）
    soup = BeautifulSoup(description_raw, "html.parser")
    img_tag = soup.find("img")
    img_url = img_tag["src"] if img_tag else "https://via.placeholder.com/300x180.png?text=No+Image"

    # リード文（HTMLタグ除去 → 先頭60文字）
    text_only = re.sub('<[^<]+?>', '', description_raw)
    summary = text_only.strip().replace("\n", "").replace("\r", "")[:60]

    articles.append({
        "title": title,
        "url": link,
        "date": pubDate[:16],
        "img": img_url,
        "summary": summary
    })

# HTML出力（カード型・2列×3行）
html = '''<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>最新記事</title>
  <style>
    body { font-family: sans-serif; padding: 1rem; background: #fff; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 1rem; }
    .card { border: 1px solid #ccc; border-radius: 8px; overflow: hidden; background: #fafafa; box-shadow: 0 2px 6px rgba(0,0,0,0.1); }
    .card img { width: 100%; height: auto; display: block; }
    .card .text { padding: .5rem; }
    .card .text h3 { font-size: 1rem; margin: 0 0 .5rem; }
    .card .text p { font-size: .85rem; color: #333; line-height: 1.4; }
    .card .text .date { font-size: .75rem; color: #888; margin-top: .5rem; }
    a { color: inherit; text-decoration: none; }
  </style>
</head>
<body>
  <div class="grid">
'''

for a in articles:
    html += f'''
    <a class="card" href="{a["url"]}" target="_blank">
      <img src="{a["img"]}" alt="thumbnail">
      <div class="text">
        <h3>{a["title"]}</h3>
        <p>{a["summary"]}...</p>
        <div class="date">{a["date"]}</div>
      </div>
    </a>
    '''

html += """
  </div>
</body>
</html>
"""

with open("note_grid.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✅ note_grid.html を生成しました（サムネイル＋リード文カード表示）")
