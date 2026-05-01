#!/usr/bin/env python3
"""Move design screenshot inside the wrap div."""

from pathlib import Path

HTML_PATH = Path("/Users/matsumaepc/Desktop/Claude code/jozu-flag-lp.html")

html = HTML_PATH.read_text(encoding="utf-8")
lines = html.split('\n')

# Find the design section structure
# We need to move the screenshot block (lines ~1178-1185) to BEFORE the wrap closes
# Current structure (0-indexed, so line N is index N-1):
#   index 1174 (line 1175):     </div>  <- closes design__inner
#   index 1175 (line 1176):   </div>    <- closes wrap
#   index 1176 (line 1177): empty
#   index 1177 (line 1178):     <!-- Design catalog screenshot -->
#   ...
#   index 1185 (line 1186): empty
#   index 1186 (line 1187): </section>

# Find the indices
design_inner_close = None
wrap_close = None
screenshot_start_idx = None
screenshot_end_idx = None

for i, line in enumerate(lines):
    if '<!-- Design catalog screenshot -->' in line:
        screenshot_start_idx = i
    if screenshot_start_idx is not None and screenshot_end_idx is None:
        if line.strip() == '</div>' and i > screenshot_start_idx:
            screenshot_end_idx = i

# Now find the wrap close BEFORE the screenshot
for i in range(screenshot_start_idx - 1, max(0, screenshot_start_idx - 10), -1):
    if lines[i].strip() == '</div>' and wrap_close is None:
        wrap_close = i
    elif lines[i].strip() == '</div>' and design_inner_close is None:
        design_inner_close = i
        break

print(f"design_inner_close: {design_inner_close + 1} = '{lines[design_inner_close]}'")
print(f"wrap_close: {wrap_close + 1} = '{lines[wrap_close]}'")
print(f"screenshot: lines {screenshot_start_idx+1}–{screenshot_end_idx+1}")

# Extract screenshot block (lines from screenshot_start to screenshot_end inclusive)
screenshot_lines = lines[screenshot_start_idx:screenshot_end_idx + 1]

# Build new lines:
# Keep everything up to and including design_inner_close
new_lines = lines[:design_inner_close + 1]
# Add screenshot block INSIDE wrap (after design__inner closes, before wrap closes)
new_lines.append('')
for l in screenshot_lines:
    new_lines.append(l)
new_lines.append('')
# Add wrap close
new_lines.append(lines[wrap_close])
# Skip the original wrap_close to screenshot_end+1 range
# Then add </section> and the rest
# Find the </section> after the screenshot
section_close_idx = None
for i in range(screenshot_end_idx + 1, screenshot_end_idx + 10):
    if i < len(lines) and lines[i].strip() == '</section>':
        section_close_idx = i
        break

if section_close_idx is None:
    print("ERROR: couldn't find </section>")
    exit(1)

print(f"section_close: {section_close_idx+1} = '{lines[section_close_idx]}'")

new_lines.append(lines[section_close_idx])
# Add everything after section_close
new_lines.extend(lines[section_close_idx + 1:])

new_html = '\n'.join(new_lines)
HTML_PATH.write_text(new_html, encoding="utf-8")
print(f"Done! File size: {len(new_html)//1024}KB")

# Verify
with open(HTML_PATH, encoding='utf-8') as f:
    fixed = f.readlines()
for i, line in enumerate(fixed):
    if 'INDUSTRY' in line and '<!--' in line and i > 700:
        print(f"\nContext around INDUSTRY (line {i+1}):")
        for j in range(max(700,i-16), i+3):
            s = fixed[j].rstrip()
            if len(s) > 80: s = s[:60] + '...'
            print(f"  {j+1}: {s}")
        break
