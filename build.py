#!/usr/bin/env python3
"""
Build the scratchd.net site from the pages in the innovatory repo.

The Scratchd pages are authored in ../innovatory/scratchd/. This copies them
here and rewrites the few things that differ on a standalone domain:

  - paths lose a directory level, because the product page sits at the root
  - links back to the lab become absolute, to innovatory.xyz
  - canonical, og:url and the JSON-LD url point at scratchd.net

Edit the pages in innovatory. Run this. Commit here.

Every rewrite below is asserted, so if a page changes shape in innovatory and
a rule stops matching, this stops with an error instead of quietly shipping a
half-rewritten page.
"""

import pathlib
import shutil
import sys

DST = pathlib.Path(__file__).resolve().parent
SRC = DST.parent / "innovatory"
LAB = "https://innovatory.xyz/"
SITE = "https://scratchd.net/"

if not (SRC / "scratchd" / "index.html").exists():
    sys.exit(f"Cannot find the innovatory repo at {SRC}")


def rewrite(src_rel, dst_rel, rules):
    text = (SRC / src_rel).read_text(encoding="utf-8")
    for old, new in rules:
        if old not in text:
            sys.exit(f"{src_rel}: expected to find {old!r} and did not. "
                     "The page changed shape; update build.py.")
        text = text.replace(old, new)
    out = DST / dst_rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"  {src_rel} -> {dst_rel}")


# The cross-reference back to the copy on innovatory.xyz, appended to the
# footer note that is already there.
FOOTER_ANCHOR = """        Your notes are files in a folder you chose. Innovatory does not run a server that holds them.
      </p>"""
FOOTER_WITH_XREF = FOOTER_ANCHOR + """
      <p class="footer-note">
        This page also lives at <a href="https://innovatory.xyz/scratchd/">innovatory.xyz/scratchd</a>.
      </p>"""

print("Pages:")

rewrite("scratchd/index.html", "index.html", [
    ("../assets/", "assets/"),
    ("../theme.js", "theme.js"),
    ('href="../feed.xml"', f'href="{LAB}feed.xml"'),
    ('href="../"', f'href="{LAB}"'),
    ("https://innovatory.xyz/assets/scratchd/icon-512.png",
     f"{SITE}assets/scratchd/icon-512.png"),
    ("https://innovatory.xyz/scratchd/", SITE),
    (FOOTER_ANCHOR, FOOTER_WITH_XREF),
])

for page in ("privacy", "support", "compare"):
    rewrite(f"scratchd/{page}/index.html", f"{page}/index.html", [
        ("../../assets/", "../assets/"),
        ("../../theme.js", "../theme.js"),
        ('href="../../feed.xml"', f'href="{LAB}feed.xml"'),
        ('href="../../"', f'href="{LAB}"'),
        # No canonical rewrite here. Both copies of these pages already declare
        # scratchd.net as canonical, so the innovatory copy points here too.
    ])

print("Files:")

for src_rel, dst_rel in [
    ("scratchd/scratchd.css", "scratchd.css"),
    ("theme.js", "theme.js"),
    ("assets/logo-64.png", "assets/logo-64.png"),
    ("assets/scratchd/icon-128.png", "assets/scratchd/icon-128.png"),
    ("assets/scratchd/icon-256.png", "assets/scratchd/icon-256.png"),
    ("assets/scratchd/icon-512.png", "assets/scratchd/icon-512.png"),
]:
    out = DST / dst_rel
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SRC / src_rel, out)
    print(f"  {dst_rel}")

shots_src = SRC / "assets" / "scratchd" / "shots"
shots_dst = DST / "assets" / "scratchd" / "shots"
shots_dst.mkdir(parents=True, exist_ok=True)
count = 0
for shot in sorted(shots_src.glob("*.jpg")):
    shutil.copy2(shot, shots_dst / shot.name)
    count += 1
print(f"  assets/scratchd/shots/ ({count} images)")

(DST / "CNAME").write_text("scratchd.net\n", encoding="utf-8")
print("  CNAME")

print("\nDone.")
