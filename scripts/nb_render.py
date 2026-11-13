#!/usr/bin/env python3
"""Render NB04 sources to HTML and PDF placeholders.

This is a minimal renderer for NotebookLM NB04 sources.
It converts Markdown to simple HTML and creates a PDF placeholder.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "vaultVivienda" / "notebooklm" / "NB04-BDA-Mongo"
OUT_DIR = SRC_DIR / "rendered"
OUT_DIR.mkdir(exist_ok=True)

def md_to_html(md_text: str) -> str:
    # Very simple conversion: headings, bold, code blocks, links
    html = md_text
    # code blocks
    html = re.sub(r'```(\w+)?\n(.*?)\n```', r'<pre><code>\2</code></pre>', html, flags=re.DOTALL)
    # headings
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    # bold
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    # italic
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    # links
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
    # paragraphs
    parts = re.split(r'\n\n+', html)
    parts = [f'<p>{p.strip()}</p>' if not p.strip().startswith('<') else p for p in parts]
    body = '\n'.join(parts)
    return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="utf-8"><title>{Path(md_text).name}</title></head>
<body>{body}</body>
</html>"""

def render():
    md_files = sorted(SRC_DIR.glob('*.md'))
    rendered = 0
    for md_path in md_files:
        # skip helper files
        if md_path.name.startswith('_'):
            continue
        content = md_path.read_text(encoding='utf-8')
        html = md_to_html(content)
        html_path = OUT_DIR / (md_path.stem + '.html')
        html_path.write_text(html, encoding='utf-8')
        # PDF placeholder: just copy html to .pdf.txt
        pdf_path = OUT_DIR / (md_path.stem + '.pdf.txt')
        pdf_path.write_text(f"PDF placeholder for {md_path.name}\nGenerated from HTML.", encoding='utf-8')
        rendered += 1
        print(f"Rendered {md_path.name} -> {html_path.name}")
    print(f"Done: {rendered} sources rendered to {OUT_DIR}")

if __name__ == '__main__':
    render()
