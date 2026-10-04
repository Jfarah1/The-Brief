#!/usr/bin/env python3
"""Sanity-check an issue before publishing.

Usage: python3 scripts/check_issue.py issues/YYYY-MM-DD.html

Counts ledger rows (<tr data-type="indep|state|main">), reports the
non-mainstream share, and fails if it is under 50% or if the share printed
in the issue doesn't match the ledger. Also flags story cards that have
fewer than two perspective blocks.
"""
import re
import sys

path = sys.argv[1]
html = open(path, encoding="utf-8").read()
errors = []

types = re.findall(r'<tr data-type="(indep|state|main)"', html)
indep = sum(t in ("indep", "state") for t in types)
main = types.count("main")
total = len(types)
if total == 0:
    errors.append("ledger has no rows")
    pct = 0
else:
    pct = round(100 * indep / total)
print(f"ledger: {indep} non-mainstream + {main} mainstream = {total} sources -> {pct}% non-mainstream")

if total and pct < 50:
    errors.append(f"non-mainstream share {pct}% is below the 50% floor")

printed = re.search(r'<div class="big-pct">(\d+)%</div>', html)
if not printed:
    errors.append("missing big-pct in ledger summary")
elif int(printed.group(1)) != pct:
    errors.append(f"ledger summary says {printed.group(1)}% but rows give {pct}%")

footnote = re.search(r"(\d+) independent / international / state, and (\d+) mainstream, out of (\d+) sources", html)
if footnote and tuple(map(int, footnote.groups())) != (indep, main, total):
    errors.append(f"ledger footnote counts {footnote.groups()} don't match rows ({indep}, {main}, {total})")

badge = re.search(r'class="indep-badge">(\d+)%', html)
if badge and int(badge.group(1)) != pct:
    errors.append(f"masthead badge says {badge.group(1)}% but ledger gives {pct}%")

for story in re.findall(r'<article class="story" id="([^"]+)">(.*?)</article>', html, re.S):
    sid, body = story
    views = len(re.findall(r'class="view [abc]"', body))
    if views < 2:
        errors.append(f"story {sid} has {views} perspective block(s); needs 2+ (or a one-sided flag)")

if errors:
    print("FAIL")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print("OK")
