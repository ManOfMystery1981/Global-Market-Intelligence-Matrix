#!/usr/bin/env python3
"""
seo_optimization_bot.py - Generates SEO-optimized HTML pages and sitemap.
"""

import os
import time
import json
import markdown
from datetime import datetime

def create_seo_html_page(keyword, content, output_dir="./posts"):
    """Generate an SEO-optimized HTML page from markdown content."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Convert markdown to HTML
    html_content = markdown.markdown(content)
    
    # Create SEO metadata
    title = f"{keyword} - Global Market Intelligence Matrix"
    description = f"Real-time data-arbitrage analytics for {keyword} from Global Market Intelligence Matrix."
    
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <meta name="robots" content="index, follow">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:type" content="article">
    <meta name="twitter:card" content="summary">
    <link rel="canonical" href="https://manofmystery1981.github.io/global-software-trends/posts/{keyword}.html">
    <style>
        body {{
            background: #0a0e14;
            color: #00ff66;
            font-family: 'Courier New', monospace;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            line-height: 1.6;
        }}
        a {{ color: #00bfff; }}
        a:hover {{ color: #00ff66; }}
        h1, h2, h3 {{ color: #ffffff; border-bottom: 1px solid #00ff6633; padding-bottom: 10px; }}
        .back-link {{ margin-top: 40px; display: block; text-align: center; }}
        .back-link a {{ color: #00ff66; text-decoration: none; border: 1px solid #00ff6633; padding: 10px 20px; border-radius: 6px; }}
        .back-link a:hover {{ background: #00ff6611; }}
        .publish-date {{ color: #94a3b8; font-size: 14px; }}
    </style>
</head>
<body>
    <h1>📊 {keyword}</h1>
    <p class="publish-date">📅 Published: {datetime.now().strftime('%Y-%m-%d')}</p>
    <hr style="border-color: #00ff6633;">
    {html_content}
    <hr style="border-color: #00ff6633;">
    <div class="back-link">
        <a href="https://manofmystery1981.github.io/global-software-trends/">⬅️ Back to Home</a>
    </div>
</body>
</html>"""
    
    # Write the HTML file
    file_path = os.path.join(output_dir, f"{keyword}.html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_template)
    
    print(f"✅ SEO Bot compiled static optimization page file: {file_path}")
    return file_path

def create_sitemap():
    """Generate a sitemap.xml file listing all posts."""
    posts_dir = "./posts"
    sitemap_path = "./sitemap.xml"
    
    if not os.path.exists(posts_dir):
        print("⚠️ No posts directory found. Skipping sitemap.")
        return
    
    html_files = [f for f in os.listdir(posts_dir) if f.endswith('.html')]
    
    if not html_files:
        print("⚠️ No HTML files found in posts directory. Skipping sitemap.")
        return
    
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for file in html_files:
        url = f"https://manofmystery1981.github.io/global-software-trends/posts/{file}"
        sitemap += '  <url>\n'
        sitemap += f'    <loc>{url}</loc>\n'
        sitemap += f'    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>\n'
        sitemap += '  </url>\n'
    
    # Add home page
    sitemap += '  <url>\n'
    sitemap += '    <loc>https://manofmystery1981.github.io/global-software-trends/</loc>\n'
    sitemap += f'    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>\n'
    sitemap += '  </url>\n'
    
    sitemap += '</urlset>'
    
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(sitemap)
    
    print(f"✅ Sitemap generated: {sitemap_path}")
    return sitemap_path

if __name__ == "__main__":
    # Test run
    test_keywords = ["SolanaEngine", "DataArbitrage", "MultiAgentSys"]
    for kw in test_keywords:
        create_seo_html_page(kw, f"## {kw}\n\nThis is an automated SEO-optimized page for **{kw}**.\n\n* Real-time metrics\n* Trending data\n* Autonomous updates")
    create_sitemap()
