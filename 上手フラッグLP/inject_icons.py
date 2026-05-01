#!/usr/bin/env python3
"""Replace emoji icons with silhouette PNG illustrations."""

import base64
from pathlib import Path

HTML_PATH = Path("/Users/matsumaepc/Desktop/Claude code/jozu-flag-lp.html")
ICONS_DIR = Path("/Users/matsumaepc/Desktop/Claude code/上手フラッグ/files/transparent_elements")

def b64(filename):
    data = (ICONS_DIR / filename).read_bytes()
    return base64.b64encode(data).decode()

def img_tag(filename, size=56):
    b = b64(filename)
    return f'<img src="data:image/png;base64,{b}" width="{size}" height="{size}" style="object-fit:contain" alt="">'

print("Reading HTML...")
html = HTML_PATH.read_text(encoding="utf-8")
original_len = len(html)

# --- feat section: replace emoji divs ---
# 🏄 → 案内看板 (signboard / visibility)
html = html.replace(
    '<div class="feat__card-ico">🏄</div>',
    f'<div class="feat__card-ico">{img_tag("21_icon_案内看板.png")}</div>'
)
# 🎨 → デザイン制作
html = html.replace(
    '<div class="feat__card-ico">🎨</div>',
    f'<div class="feat__card-ico">{img_tag("23_icon_デザイン制作.png")}</div>'
)
# 💡 → 店舗会社 (store appeal)
html = html.replace(
    '<div class="feat__card-ico">💡</div>',
    f'<div class="feat__card-ico">{img_tag("20_icon_店舗会社.png")}</div>'
)
# 🪃 → クルマ (car delivery / fast turnaround)
html = html.replace(
    '<div class="feat__card-ico">🪃</div>',
    f'<div class="feat__card-ico">{img_tag("17_icon_クルマ.png")}</div>'
)

# --- price section: replace emoji divs ---
# 🪃 → 整備メンテ (pole / hardware)
html = html.replace(
    '<div class="price__extra-ico">🪃</div>',
    f'<div class="price__extra-ico">{img_tag("18_icon_整備メンテ.png", 44)}</div>'
)
# 📦 → 納品配送
html = html.replace(
    '<div class="price__extra-ico">📦</div>',
    f'<div class="price__extra-ico">{img_tag("28_icon_納品配送.png", 44)}</div>'
)

# --- Update CSS for feat__card-ico to handle img instead of emoji ---
old_css = '.feat__card-ico{font-size:34px;margin-bottom:12px}'
new_css = '.feat__card-ico{font-size:34px;margin-bottom:12px;display:flex;align-items:center;justify-content:center}.feat__card-ico img{filter:invert(1) brightness(2);opacity:.9}'
html = html.replace(old_css, new_css)

# --- Update CSS for price__extra-ico ---
old_css2 = '.price__extra-ico{font-size:30px;flex-shrink:0}'
new_css2 = '.price__extra-ico{font-size:30px;flex-shrink:0;display:flex;align-items:center;justify-content:center}.price__extra-ico img{filter:invert(1) brightness(2);opacity:.9}'
html = html.replace(old_css2, new_css2)

print(f"HTML size: {original_len} → {len(html)} chars (+{len(html)-original_len})")

print("Writing modified HTML...")
HTML_PATH.write_text(html, encoding="utf-8")
print("Done!")

# Verify replacements
for emoji in ['🏄', '🎨', '💡', '🪃', '📦']:
    count = html.count(emoji)
    print(f"  Remaining '{emoji}': {count}")
