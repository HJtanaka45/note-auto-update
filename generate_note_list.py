import requests
import xml.etree.ElementTree as ET
from html import escape
from datetime import datetime

RSS_URL = "https://note.com/saiwainomori/rss"

response = requests.get(RSS_URL)
root = ET.fromstring(response.content)
channel = root.find('channel')
all_items = channel.findall('item')

# カテゴリごとに分ける辞書
categorized = {}

# 最新6件を保存
latest_items = []

# note_simple.html 用（タイトル＋日付だけ）
simple_list = []

for i, item in enumerate(all_items):
    title = item.find('title').text
    link = item.find('link').text
    pub_date_raw = item.find('pubDate').text
    pub_date = datetime.strptime(pub_date_raw, "%a, %d %b %Y %H:%M:%S %z")
    pub_date_str = pub_date.strftime("%a, %d %b %Y")

    description = item.find('description').text or ""
    # OGP画像取得
    if 'https://' in description and ('.jpg' in description or '.jpeg' in description or '.png' in description):
        start = description.find('https')
        end = description.find('.jpg')
        if end == -1:
            end = description.find('.jpeg')
        if end == -1:
            end = description.find('.png')
        if end != -1:
            image_url = description[start:end+4]
        else:
            image_url = ""
    else:
        image_url = ""

    # リード文取得（30文字以内に整える）
    lead = description.replace('<br>', '').replace('\u3000', ' ').replace('\n', ' ').strip()
    if len(lead) > 50:
        lead = lead[:48] + "..."

    # カテゴリ取得（note特有）
    category_el = item.find('category')
    category = category_el.text if category_el is not None else "未分類"

    if category not in categorized:
        categorized[category] = []

    categorized[category].append(f'<li><a href="{link}">{escape(title)}</a> <span>{pub_date_str}</span></li>')

    # 最新6件（note_grid.html用）
    if i < 6:
        latest_items.append(f'''
        <div class="card">
            <a href="{link}" target="_blank">
                {f'<img src="{image_url}" alt="サムネイル" />' if image_url else ''}
                <div class="text-area">
                    <h3>{escape(title)}</h3>
                    <p>{lead}</p>
                    <span>{pub_date_str}</span>
                </div>
            </a>
        </div>
        ''')

    # note_simple.html 用
    simple_list.append(f'<li>{pub_date_str} - <a href="{link}" target="_blank">{escape(title)}</a></li>')

# note_list.html 出力
with open("note_list.html", "w", encoding="utf-8") as f:
    f.write("""
    <html><head><meta charset="utf-8"><title>Note一覧</title></head><body>
    <h1>記事一覧（カテゴリ別）</h1>
    """)
    for cat, links in categorized.items():
        f.write(f'<h2>{cat}</h2><ul>' + "\n".join(links) + '</ul>')
    f.write("</body></html>")

# note_grid.html 出力
with open("note_grid.html", "w", encoding="utf-8") as f:
    f.write("""
    <html><head><meta charset="utf-8">
    <title>最新記事</title>
    <style>
    body { font-family: sans-serif; text-align:center; }
    .card { border:1px solid #ccc; border-radius:6px; padding:1em; margin:1em; width:300px; display:inline-block; vertical-align:top; box-shadow:2px 2px 8px #ccc; }
    img { max-width:100%; height:auto; }
    .text-area { text-align:left; }
    h3 { font-size:1.1em; margin-bottom:0.2em; }
    p { font-size:0.9em; color:#333; margin:0.2em 0 0.5em; }
    span { font-size:0.8em; color:gray; }
    </style></head><body>
    <h2>最新記事</h2>
    """)
    f.write("\n".join(latest_items))
    f.write("</body></html>")

# note_simple.html 出力
with open("note_simple.html", "w", encoding="utf-8") as f:
    f.write("""
    <html><head><meta charset="utf-8"><title>記事一覧（シンプル）</title></head><body>
    <h1>記事一覧（タイトルと日付のみ）</h1><ul>
    """)
    f.write("\n".join(simple_list))
    f.write("</ul></body></html>")
