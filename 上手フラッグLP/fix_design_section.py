#!/usr/bin/env python3
"""Fix the design section structure - move orphaned screenshot inside section."""

from pathlib import Path

HTML_PATH = Path("/Users/matsumaepc/Desktop/Claude code/jozu-flag-lp.html")

print("Reading HTML...")
html = HTML_PATH.read_text(encoding="utf-8")

lines = html.split('\n')

# Find the orphaned pattern: after the design section closes (</section>)
# there are orphaned: </div>, design screenshot block, </div>, </section>
# before <!-- INDUSTRY -->

# We need to:
# 1. Find the INDUSTRY marker
# 2. Look backwards to find the orphaned closing tags + screenshot block
# 3. Move the screenshot INSIDE the design section

industry_idx = None
for i, line in enumerate(lines):
    if '<!-- ==================== INDUSTRY' in line:
        industry_idx = i
        break

if industry_idx is None:
    print("ERROR: INDUSTRY marker not found")
    exit(1)

print(f"INDUSTRY marker at line {industry_idx+1}")

# Look backwards from INDUSTRY to find the orphaned </section>
# The pattern should be (going backward from INDUSTRY):
# </section>  <- orphaned
# </div>      <- orphaned
# ... screenshot block ...
# </div>      <- orphaned
# empty line
# </section>  <- correct design section close
# </div>      <- correct wrap close
# </div>      <- correct design__inner close

# Find the design section's correct </section>
# by finding the FIRST </section> before INDUSTRY
orphaned_section_idx = None
for i in range(industry_idx - 1, max(0, industry_idx - 30), -1):
    if lines[i].strip() == '</section>':
        orphaned_section_idx = i
        print(f"  Orphaned </section> at line {i+1}: '{lines[i]}'")
        break

# Find the real design </section> (one more before that)
real_section_idx = None
for i in range(orphaned_section_idx - 1, max(0, orphaned_section_idx - 30), -1):
    if lines[i].strip() == '</section>':
        real_section_idx = i
        print(f"  Real design </section> at line {i+1}: '{lines[i]}'")
        break

if orphaned_section_idx is None or real_section_idx is None:
    print("ERROR: Could not find section boundaries")
    exit(1)

# Extract the orphaned content (between the real </section> and orphaned </section>)
# This is: empty line, </div>, screenshot block, </div>, </section>
orphaned_content_lines = lines[real_section_idx + 1 : orphaned_section_idx + 1]
print(f"  Orphaned block ({len(orphaned_content_lines)} lines):")
for j, l in enumerate(orphaned_content_lines[:5]):
    print(f"    [{j}] {l[:80]}")

# Extract just the screenshot div (from <!-- Design catalog screenshot --> to its </div>)
screenshot_start = None
screenshot_end = None
for j, l in enumerate(orphaned_content_lines):
    if '<!-- Design catalog screenshot -->' in l:
        screenshot_start = j
    if screenshot_start is not None and l.strip() == '</div>' and j > screenshot_start:
        screenshot_end = j
        break

if screenshot_start is None or screenshot_end is None:
    print(f"  screenshot_start={screenshot_start}, screenshot_end={screenshot_end}")
    # Try to find the screenshot div differently
    for j, l in enumerate(orphaned_content_lines):
        if 'design__flag' not in l and ('kicker' in l or 'full15' in l or '全15種類' in l):
            screenshot_start = j - 1  # include the preceding div
            break
    # Find end
    if screenshot_start is not None:
        depth = 0
        for j in range(screenshot_start, len(orphaned_content_lines)):
            l = orphaned_content_lines[j].strip()
            if l.startswith('<div'):
                depth += 1
            elif l == '</div>':
                depth -= 1
                if depth <= 0:
                    screenshot_end = j
                    break

print(f"  Screenshot block: lines {screenshot_start} to {screenshot_end} of orphaned block")

if screenshot_start is None or screenshot_end is None:
    # Just take everything between </div> and </div> in the orphaned block
    # Find the screenshot img line
    for j, l in enumerate(orphaned_content_lines):
        if '全15種類のデザインバリエーション' in l or ('kicker' in l and j < len(orphaned_content_lines)//2):
            # go back to the enclosing <div
            for k in range(j, -1, -1):
                if '<div' in orphaned_content_lines[k]:
                    screenshot_start = k
                    break
            break
    if screenshot_start is not None:
        depth = 0
        for j in range(screenshot_start, len(orphaned_content_lines)):
            l = orphaned_content_lines[j].strip()
            depth += l.count('<div') - l.count('</div')
            if j > screenshot_start and depth <= 0:
                screenshot_end = j
                break

print(f"  Final screenshot_start={screenshot_start}, screenshot_end={screenshot_end}")

screenshot_block = '\n'.join(orphaned_content_lines[screenshot_start:screenshot_end+1])
print(f"  Screenshot block preview: {screenshot_block[:100]}")

# Now rebuild:
# Remove orphaned lines after real_section_idx
# Insert screenshot block BEFORE the real </section> of design section
# Find where the wrap </div> is before the real </section>
wrap_close_idx = real_section_idx - 1
while lines[wrap_close_idx].strip() == '':
    wrap_close_idx -= 1
print(f"  Before real section close at line {real_section_idx+1}: '{lines[wrap_close_idx]}'")

# Build new lines list
new_lines = lines[:real_section_idx]  # everything up to (not including) real </section>
# Insert screenshot block inside the wrap div
new_lines.append('')
new_lines.extend(screenshot_block.split('\n'))
new_lines.append('')
new_lines.append('</section>')  # the real section close
new_lines.append('')
# Skip the orphaned block (lines real_section_idx+1 to orphaned_section_idx inclusive)
new_lines.extend(lines[orphaned_section_idx + 1:])  # rest of file

new_html = '\n'.join(new_lines)

print(f"Writing fixed HTML... ({len(new_html)//1024}KB)")
HTML_PATH.write_text(new_html, encoding="utf-8")
print("Done!")

# Verify
with open(HTML_PATH, encoding='utf-8') as f:
    fixed = f.readlines()
for i, line in enumerate(fixed):
    if 'INDUSTRY' in line:
        print(f"\nContext around INDUSTRY (line {i+1}):")
        for j in range(max(0,i-12), min(len(fixed), i+3)):
            s = fixed[j].rstrip()
            if len(s) > 80:
                s = s[:50] + '...'
            print(f"  {j+1}: {s}")
        break
