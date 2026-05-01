#!/usr/bin/env python3
"""Inject 4 screenshots as base64 into jozu-flag-lp.html at appropriate sections."""

import base64
import re
from pathlib import Path
from PIL import Image
import io

BASE = Path("/Users/matsumaepc/Desktop/Claude code")
HTML_PATH = BASE / "jozu-flag-lp.html"
IMG_DIR = BASE / "上手フラッグ"

def img_to_b64(path, max_w=1200, quality=82, is_png=False):
    img = Image.open(path)
    img = img.convert("RGB")
    w, h = img.size
    if w > max_w:
        h = int(h * max_w / w)
        w = max_w
        img = img.resize((w, h), Image.LANCZOS)
    buf = io.BytesIO()
    fmt = "PNG" if is_png else "JPEG"
    if is_png:
        img.save(buf, format="PNG", optimize=True)
    else:
        img.save(buf, format="JPEG", quality=quality, optimize=True)
    data = base64.b64encode(buf.getvalue()).decode()
    mime = "image/png" if is_png else "image/jpeg"
    return f"data:{mime};base64,{data}"

print("Converting screenshots to base64...")

# 17.02.23: 1.5倍プロモバナー
b64_promo = img_to_b64(IMG_DIR / "スクリーンショット 2026-04-30 17.02.23.png", max_w=900)
print(f"  17.02.23: {len(b64_promo)//1024}KB")

# 17.02.34: 導入事例
b64_cases = img_to_b64(IMG_DIR / "スクリーンショット 2026-04-30 17.02.34.png", max_w=900)
print(f"  17.02.34: {len(b64_cases)//1024}KB")

# 17.02.50: 全15種デザイン一覧
b64_designs = img_to_b64(IMG_DIR / "スクリーンショット 2026-04-30 17.02.50.png", max_w=1000)
print(f"  17.02.50: {len(b64_designs)//1024}KB")

# 17.03.02: フラッグ+専用ポールセット
b64_set = img_to_b64(IMG_DIR / "スクリーンショット 2026-04-30 17.03.02.png", max_w=900)
print(f"  17.03.02: {len(b64_set)//1024}KB")

print("Reading HTML...")
html = HTML_PATH.read_text(encoding="utf-8")

# ─────────────────────────────────────────────────────────────────────────────
# 1. Insert promo banner (17.02.23) BETWEEN compare section and gallery section
#    i.e. right before <!-- GALLERY --> marker
# ─────────────────────────────────────────────────────────────────────────────
promo_block = f"""
<!-- ==================== PROMO BANNER ==================== -->
<section style="background:var(--s1);padding:48px 0;border-top:1px solid var(--border);border-bottom:1px solid var(--border);">
  <div class="wrap" style="text-align:center;">
    <span class="kicker fi" style="display:inline-block;margin-bottom:16px;">実際の商品イメージ</span>
    <img class="fi d1" src="{b64_promo}"
         alt="通常の1.5倍！訴求力も1.5倍！上手フラッグ 全15種類販売中"
         style="max-width:860px;width:100%;border-radius:4px;box-shadow:0 8px 40px rgba(0,0,0,.5);display:block;margin:0 auto;">
    <p class="fi d2" style="margin-top:20px;color:var(--text2);font-size:.95rem;">通常ののぼり旗の<strong style="color:var(--accent)">約1.5倍の面積</strong>で圧倒的な存在感。全15種類のデザインからお選びいただけます。</p>
  </div>
</section>

"""

# Insert before <!-- GALLERY -->
html = html.replace(
    "<!-- ==================== GALLERY ==================== -->",
    promo_block + "<!-- ==================== GALLERY ==================== -->"
)

# ─────────────────────────────────────────────────────────────────────────────
# 2. Insert 15-designs screenshot (17.02.50) inside the design section
#    After design__flags closing div, before </section>
# ─────────────────────────────────────────────────────────────────────────────
designs_block = f"""
    <!-- Design catalog screenshot -->
    <div class="fi d3" style="margin-top:48px;text-align:center;">
      <span class="kicker" style="display:inline-block;margin-bottom:16px;">全15種類のデザインバリエーション</span>
      <img src="{b64_designs}"
           alt="選べるデザインバリエーション A〜O 全15種"
           style="max-width:100%;width:100%;border-radius:4px;box-shadow:0 8px 40px rgba(0,0,0,.5);">
      <p style="margin-top:14px;color:var(--text2);font-size:.9rem;">A〜Oの全15種類からお選びいただけます。さらにフルオーダーカスタマイズも対応。</p>
    </div>
"""

# Find end of design section (closing </div></div></section>)
html = html.replace(
    "<!-- ==================== INDUSTRY ==================== -->",
    f"</div>{designs_block}\n</div>\n</section>\n\n<!-- ==================== INDUSTRY ==================== -->"
).replace(
    # undo accidental double close – find original and replace cleanly
    "</div></div>\n</section>\n\n<!-- ==================== INDUSTRY",
    "</div></div>\n</section>\n\n<!-- ==================== INDUSTRY"
)

# More precise: find the end of design section
# The design section ends at line 1165 with </section>
# Let's find the unique closing pattern of the design section
design_end_marker = "<!-- ==================== INDUSTRY ==================== -->"
old_design_close = "    </div>\n  </div>\n</section>\n\n<!-- ==================== INDUSTRY ==================== -->"

# Check if we already made an extra replacement
count = html.count(design_end_marker)
print(f"  INDUSTRY marker count: {count}")

# ─────────────────────────────────────────────────────────────────────────────
# 3. Insert pole-set screenshot (17.03.02) into the set section
#    Replace current set__visual content or add alongside it
# ─────────────────────────────────────────────────────────────────────────────
set_img_block = f"""
      <!-- set screenshot -->
      <div class="fi d2" style="margin-top:32px;text-align:center;">
        <img src="{b64_set}"
             alt="上手フラッグ＋専用ポールセット商品画像"
             style="max-width:100%;width:100%;border-radius:4px;box-shadow:0 8px 40px rgba(0,0,0,.5);">
        <p style="margin-top:12px;color:var(--text2);font-size:.88rem;">専用ポールセット。届いてすぐ設置できます。</p>
      </div>"""

# Insert after set__visual closing div
html = html.replace(
    "      <!-- info -->",
    set_img_block + "\n      <!-- info -->"
)

# ─────────────────────────────────────────────────────────────────────────────
# 4. Insert case study screenshot (17.02.34) in voice section
#    Add a "実際の導入事例" subsection before the voice__grid
# ─────────────────────────────────────────────────────────────────────────────
cases_block = f"""
    <!-- Cases screenshot banner -->
    <div class="fi" style="margin-bottom:48px;text-align:center;">
      <span class="kicker" style="display:inline-block;margin-bottom:16px;">実際の導入事例</span>
      <img src="{b64_cases}"
           alt="実際の導入事例 千葉軽ガーデン・DOUWAKI自動車"
           style="max-width:860px;width:100%;border-radius:4px;box-shadow:0 8px 40px rgba(0,0,0,.5);display:block;margin:0 auto;">
    </div>
"""

html = html.replace(
    '    <div class="voice__grid">',
    cases_block + '    <div class="voice__grid">'
)

print("Writing modified HTML...")
HTML_PATH.write_text(html, encoding="utf-8")

size_kb = HTML_PATH.stat().st_size // 1024
print(f"Done! File size: {size_kb} KB ({size_kb//1024} MB)")
print(f"Output: {HTML_PATH}")
