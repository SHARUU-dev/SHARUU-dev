#!/usr/bin/env python3
"""Validates README.md against the files in the repo.

    python3 scripts/check_readme.py

Checks (exit code 1 if any fail):
  - every local <img src> / markdown image / link target exists, with exact letter case
  - every SVG parses as XML, loads nothing from outside, has a <title>, and has sane dimensions
  - every <img> has alt text; no orphan assets that the README never uses
  - banned content (unfinished portfolio, placeholder contact details) is absent
External URLs are listed, not fetched (they can only be tested from a machine with internet).
"""
import os
import re
import sys
import xml.dom.minidom as minidom

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
readme = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
errors, notes = [], []


def exact_exists(rel):
    cur = ROOT
    for part in rel.split("/"):
        if part not in os.listdir(cur):
            return False
        cur = os.path.join(cur, part)
    return os.path.exists(cur)


body = re.sub(r"<!--.*?-->", "", readme, flags=re.S)
imgs = re.findall(r"<img\b[^>]*>", body)
local, external = set(), set()
for tag in imgs:
    src = re.search(r'src="([^"]+)"', tag)
    alt = re.search(r'alt="([^"]*)"', tag)
    if not src:
        errors.append(f"img without src: {tag[:60]}")
        continue
    if not alt or not alt.group(1).strip():
        errors.append(f"missing alt text: {src.group(1)}")
    (external if src.group(1).startswith("http") else local).add(src.group(1))
for href in re.findall(r'href="([^"]+)"', body) + re.findall(r"\]\(([^)\s]+)\)", body):
    (external if href.startswith(("http", "mailto:")) else local).add(href)

for rel in sorted(local):
    if rel.startswith("#"):
        continue
    if not exact_exists(rel):
        errors.append(f"broken local path (check spelling and capitalisation): {rel}")

used = {os.path.basename(p) for p in local if p.startswith("assets/")}
for f in sorted(os.listdir(os.path.join(ROOT, "assets"))):
    if f.endswith(".svg") and f not in used:
        errors.append(f"orphan asset never referenced by README: assets/{f}")

for f in sorted(os.listdir(os.path.join(ROOT, "assets"))):
    if not f.endswith(".svg"):
        continue
    p = os.path.join(ROOT, "assets", f)
    raw = open(p, encoding="utf-8").read()
    try:
        doc = minidom.parseString(raw)
    except Exception as e:  # noqa: BLE001
        errors.append(f"{f}: invalid XML ({e})")
        continue
    root = doc.documentElement
    if not doc.getElementsByTagName("title"):
        errors.append(f"{f}: no <title> (accessibility)")
    for bad in ("<image", "<script", "foreignObject", "@import", "url(http", 'href="http', "xlink:href"):
        if bad in raw:
            errors.append(f"{f}: contains '{bad}' (not allowed: keeps SVGs self-contained and GitHub-safe)")
    w, h = float(root.getAttribute("width")), float(root.getAttribute("height"))
    if w > 900 or h > 500:
        errors.append(f"{f}: {w:.0f}x{h:.0f} is oversized for a README column")
    if os.path.getsize(p) > 150_000:
        errors.append(f"{f}: {os.path.getsize(p)//1024} KB is heavy")

banned = [r"portfolio", r"sharuux-2007\.github\.io", r"example\.com", r"your-email", r"lorem", r"todo", r"placeholder"]
for pat in banned:
    for target, text in (("README.md", readme), *[(f"assets/{f}", open(os.path.join(ROOT, 'assets', f), encoding='utf-8').read())
                                                  for f in os.listdir(os.path.join(ROOT, "assets")) if f.endswith(".svg")]):
        if re.search(pat, text, re.I) and not (pat == "placeholder" and target == "assets/snake-dark.svg"):
            errors.append(f"banned text /{pat}/ found in {target}")

print(f"{len(imgs)} images, {len(local)} local references, {len(external)} external URLs")
for u in sorted(external):
    print("  external (not fetched):", u)
if errors:
    print("\nFAILED:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print("\nOK: all local paths resolve (case-exact), all SVGs valid and self-contained.")
