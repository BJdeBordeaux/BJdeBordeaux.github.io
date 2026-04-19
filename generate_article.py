#!/usr/bin/env python3
import sys; sys.stdout.reconfigure(encoding='utf-8')
"""
生成静态文章页（og:image 直接写入 HTML，微信分享正常显示）
用法: python generate_article.py "文章标题"
      python generate_article.py --all
"""
import os, sys, re, html

SITE = "https://BJdeBordeaux.github.io"
IMAGES_DIR = "images"
CSS_FILE = "../css/style.css"

SHARE_SVG = '''<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>'''

def get_og_image(content, explicit_image, filename):
    """Determine the og:image URL"""
    if explicit_image:
        src = explicit_image.strip()
        if src.startswith('http'):
            return src
        return f"{SITE}/{src.lstrip('/')}"
    # Auto-detect first markdown image
    m = re.search(r'!\[.*?\]\((.*?)\)', content)
    if m:
        src = m.group(1).strip()
        if src.startswith('http'):
            return src
        return f"{SITE}/{src.lstrip('/')}"
    return f"{SITE}/{IMAGES_DIR}/default-cover.jpg"

def slugify(title):
    """Convert title to safe HTML filename"""
    # Remove/replace special chars, keep Chinese
    s = re.sub(r'[<>:"/\\|?*]', '', title)
    s = s.strip() + '.html'
    return s

def parse_frontmatter(text):
    """Parse YAML front-matter, return (meta dict, body content)"""
    if not text.startswith('---'):
        return {}, text
    end = text.index('---', 3)
    if end == -1:
        return {}, text
    yaml_text = text[3:end].strip()
    body = text[end+3:].strip()
    meta = {}
    for line in yaml_text.splitlines():
        colon = line.index(':')
        if colon == -1:
            continue
        key = line[:colon].strip()
        val = line[colon+1:].strip()
        meta[key] = val
    return meta, body

def render_markdown(body):
    """Lightweight markdown->HTML renderer"""
    lines = body.splitlines()
    html_parts = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # hr
        if re.match(r'^(-{3,}|\*{3,}|_{3,})$', line.strip()):
            html_parts.append('<hr>')
            i += 1
            continue
        # blockquote
        if line.strip().startswith('>'):
            html_parts.append('<blockquote>' + html.escape(line.lstrip('>').strip()) + '</blockquote>')
            i += 1
            continue
        # heading
        hm = re.match(r'^(#{1,6})\s+(.*)', line)
        if hm:
            level = len(hm.group(1))
            html_parts.append(f'<h{level}>{render_inline(hm.group(2))}</h{level}>')
            i += 1
            continue
        # paragraph
        if line.strip():
            html_parts.append(f'<p>{render_inline(line)}</p>')
        i += 1
    return '\n'.join(html_parts)

def render_inline(text):
    """Render inline markdown: bold, italic, links, images"""
    # image: ![alt](src)
    text = re.sub(r'!\[(.*?)\]\((.*?)\)', r'<img src="\2" alt="\1" style="max-width:100%;border-radius:8px;margin:1em 0;">', text)
    # link: [text](url)
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" target="_blank" rel="noopener">\1</a>', text)
    # bold+italic
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    # bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # italic
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    return text

def build_article_html(meta, body, article_url, filename):
    body_html = render_markdown(body)
    title = meta.get('title', '无标题')
    tag   = meta.get('tag', '')
    date  = meta.get('date', '')
    desc  = meta.get('desc', meta.get('description', ''))
    og_img = get_og_image(body_html, meta.get('image', ''), filename)
    body_html = render_markdown(body)

    # Escape for JS string
    title_js  = title.replace('\\', '\\\\').replace("'", "\\'").replace('\n', ' ')
    desc_js   = desc.replace('\\', '\\\\').replace("'", "\\'").replace('\n', ' ')

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} · 梁飞飞</title>

  <!-- Open Graph / WeChat Card -->
  <meta property="og:title"       content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:image"       content="{og_img}">
  <meta property="og:url"        content="{article_url}">
  <meta property="og:type"       content="article">

  <!-- Twitter Card -->
  <meta name="twitter:card"        content="summary_large_image">
  <meta name="twitter:title"       content="{title}">
  <meta name="twitter:description" content="{desc}">
  <meta name="twitter:image"       content="{og_img}">

  <link rel="stylesheet" href="{CSS_FILE}">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🌿</text></svg>">
</head>
<body>

  <header>
    <div class="container">
      <a href="index.html" class="site-title">梁飞飞<span>·</span>写东西的地方</a>
      <p class="tagline">大巴黎 · 程序员 · 偶尔写写</p>
    </div>
  </header>

  <div class="divider"></div>

  <main class="container">
    <article class="article-page">
      <a href="index.html" class="article-back">← 返回首页</a>
      <header class="article-header">
        <h1>{title}</h1>
        <div class="article-meta">
          <span class="meta-tag">{tag}</span>
          <span class="meta-date">{date}</span>
        </div>
      </header>
      <div class="article-body">
        {body_html}
      </div>

      <!-- Share -->
      <div class="share-section">
        <p class="share-label">转发给朋友</p>
        <div class="share-btns">
          <button class="share-btn share-native" id="shareNative" title="分享">
            {SHARE_SVG}
            分享
          </button>
        </div>
      </div>
    </article>
  </main>

  <footer>
    <div class="container">
      © 2026 梁飞飞 · 写得随意，读得开心
    </div>
  </footer>

  <script>
    (function() {{
      const title = '{title_js}';
      const url   = location.href;
      document.getElementById('shareNative').addEventListener('click', async () => {{
        if (navigator.share) {{
          try {{ await navigator.share({{ title, url }}); }} catch(e) {{}}
        }} else {{
          navigator.clipboard.writeText(url);
        }}
      }});
    }})();
  </script>

</body>
</html>
'''

def process_md(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    meta, body = parse_frontmatter(text)
    title = meta.get('title', os.path.splitext(os.path.basename(filepath))[0])
    filename = slugify(title)
    article_url = f"{SITE}/{filename}"

    html = build_article_html(meta, body, article_url, filename)

    out_path = os.path.join(os.path.dirname(filepath), filename)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  生成: {out_path}")
    return filename, title, meta

def main():
    articles_dir = 'articles'

    if '--all' in sys.argv or len(sys.argv) == 1:
        print("生成所有文章页面…")
        md_files = sorted([f for f in os.listdir(articles_dir) if f.endswith('.md')], reverse=True)
        for md in md_files:
            process_md(os.path.join(articles_dir, md))
        print("完成！")
        return

    # Single article by title
    title_arg = sys.argv[1]
    md_files = [f for f in os.listdir(articles_dir) if f.endswith('.md')]
    for mf in md_files:
        if title_arg in mf or title_arg == mf.replace('.md', ''):
            process_md(os.path.join(articles_dir, mf))
            print("完成！")
            return
    print(f"未找到文章: {title_arg}")

if __name__ == '__main__':
    main()
