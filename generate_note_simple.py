# generate_note_simple.py
import feedparser
from datetime import datetime

# RSSフィードURL（note公式）
rss_url = "https://note.com/saiwainomori/rss"
feed = feedparser.parse(rss_url)

# HTMLヘッダー＋CSS内包
html_head = '''<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <title>NOTE記事一覧</title>
  <style>
    body {
      margin: 0;
      padding: 20px 10px;
      font-family: "游ゴシック", "Hiragino Kaku Gothic Pro", sans-serif;
      background: #fff;
      color: #333;
      font-size: 16px;
      line-height: 1.7;
    }
    ul.note-simple-list {
      list-style: none;
      padding: 0;
      margin: 0;
    }
    ul.note-simple-list li {
      border-bottom: 1px solid #e5e5e5;
      padding: 14px 8px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    ul.note-simple-list li a {
      color: #226622;
      text-decoration: none;
      flex-grow: 1;
      font-weight: 500;
    }
    ul.note-simple-list li a:hover {
      text-decoration: underline;
    }
    .date {
      color: #666;
      font-size: 14px;
      white-space: nowrap;
      margin-left: 1em;
    }
    @media (max-width: 600px) {
      ul.note-simple-list li {
        flex-direction: column;
        align-items: flex-start;
      }
      .date {
        margin-left: 0;
        margin-top: 4px;
      }
    }
  </style>
</head>
<body>
  <ul class="note-simple-list">
'''

# HTML記事リスト生成
html_body = ""
for entry in feed.entries:
    title = entry.title
    link = entry.link
    # 日付を「2025年7月11日」形式に整形
    published = datetime(*entry.published_parsed[:6])
    date_str = f"{published.year}年{published.month}月{published.day}日"
    html_body += f'    <li><a href="{link}" target="_blank">{title}</a><span class="date">{date_str}</span></li>\n'

# HTMLフッター
html_tail = '''  </ul>
</body>
</html>
'''

# ファイル出力
with open("note_simple.html", "w", encoding="utf-8") as f:
    f.write(html_head + html_body + html_tail)
