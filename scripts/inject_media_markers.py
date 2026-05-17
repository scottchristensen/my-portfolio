#!/usr/bin/env python3
"""Insert `[[MEDIA:...]]` placeholder markers into rich-text fields of data/work.csv.

Re-runnable: removes any existing markers first, then re-inserts based on the
INSERTIONS table below. Edit/add anchors here, run, then `python3 scripts/build_work.py`.
"""

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data" / "work.csv"

# (slug, field, anchor, marker)
# Anchor must occur exactly once in the field; the marker is inserted *after* it.
# If anchor isn't found, the marker is appended to the end of the field.
INSERTIONS = [
    # ------------------------- Mystery Onboarding -------------------------
    ("mystery-onboarding", "Background",
     "until they get there. </p>",
     "[[MEDIA:video|Mystery promo|https://vimeo.com/391423749]]"),
    ("mystery-onboarding", "Background",
     "for a discounted rate</li></ol>",
     "[[MEDIA:image|Lyft Concierge ride-flow screenshot]]"),
    ("mystery-onboarding", "Background",
     "Clearly communicate our value props &amp; updated branding</li></ul>",
     "[[MEDIA:figma|Onboarding flow (Figma)]]"),
    ("mystery-onboarding", "My Process",
     "felt like a shakedown. </p>",
     "[[MEDIA:image|Account-creation UX audit screens]]"),
    ("mystery-onboarding", "My Process",
     "Ask only the bare minimum of the user at the outset</li></ul>",
     "[[MEDIA:image|Suggested account-creation flow]]"),
    ("mystery-onboarding", "My Process",
     "always the most fun part for users. </p>",
     "[[MEDIA:image|Profile enrichment moved to end-of-flow]]"),
    ("mystery-onboarding", "My Process",
     "we saw adoption increase by 10%. </p>",
     "[[MEDIA:figma|Final onboarding prototype (Figma)]]"),

    # ------------------------- Egencia Onboarding -------------------------
    ("egencia-onboarding", "Background",
     "even a 1% contact reduction would lead to $1.5M in savings. </p>",
     "[[MEDIA:image|Call volume by country]]"),
    ("egencia-onboarding", "Background",
     "(booking for big company events -- trainings, offsites)</li></ul>",
     "[[MEDIA:image|Egencia traveler personas]]"),
    ("egencia-onboarding", "Background",
     "What does the company want/expect?</strong></li></ol>",
     "[[MEDIA:image|Strategy considerations (4 lenses)]]"),
    ("egencia-onboarding", "Background",
     "Evangelize friction-reduction</li></ol>",
     "[[MEDIA:image|Team charters + feature bets]][[MEDIA:image|Value × Effort prioritization]]"),
    ("egencia-onboarding", "My Process",
     "Option 3: Simple and Straightforward</h3>",
     "[[MEDIA:image|Help-center variants A/B/C]]"),
    ("egencia-onboarding", "My Process",
     "We rolled it out globally. </p>",
     "[[MEDIA:image|Multivariant test results]]"),

    # ----------------------- H1 Browser Extension -------------------------
    ("h1-browser-extension", "My Process",
     "yet because it seemed daunting.</p>",
     "[[MEDIA:image|Customer discovery interview (Dartmouth)]]"),
    ("h1-browser-extension", "My Process",
     "to help source further customer discovery interviews. </p>",
     "[[MEDIA:image|Fake Door landing page test]][[MEDIA:figma|H1 Explorer (Figma)]]"),
    ("h1-browser-extension", "My Process",
     "🎉 Success! Of the cohort who clicked \"Test it out\", we saw a 15% lift in usage over the next month.</p>",
     "[[MEDIA:figma|Top-of-funnel onboarding tab (Figma)]]"),
    ("h1-browser-extension", "My Process",
     "we will increase user sign-up conversion. </p>",
     "[[MEDIA:image|Rate-limit / paywall design]]"),
    ("h1-browser-extension", "My Process",
     "refine our value proposition on our marketing landing page. </p>",
     "[[MEDIA:figma|Landing-page hero variants (Figma)]]"),

    # -------------------------- H1 Doctor Profile -------------------------
    ("h1-doctor-profile", "Background",
     "serves the top Pharma companies around the world.</p>",
     "[[MEDIA:image|H1 platform overview]]"),
    ("h1-doctor-profile", "Background",
     "How can I find doctors who treat ethnically-diverse patients?\"</li></ul>",
     "[[MEDIA:image|MSL value-prop diagram]]"),
    ("h1-doctor-profile", "Background",
     "after Covid shutdown.</li></ul>",
     "[[MEDIA:image|Legacy profile UX audit issues]]"),
    ("h1-doctor-profile", "My Process",
     "based on their recent research focus.</li></ul>",
     "[[MEDIA:image|Customer discovery interview]]"),
    ("h1-doctor-profile", "My Process",
     "Use <strong id=\"\">sticky elements upon scroll</strong> (e.g. CTA, nav)</li></ul>",
     "[[MEDIA:image|Competitor audit (LinkedIn, Pitchbook, etc.)]]"),
    ("h1-doctor-profile", "My Process",
     "card sorting exercise in Miro. </p>",
     "[[MEDIA:image|Card-sorting design studio (Miro)]]"),
    ("h1-doctor-profile", "My Process",
     "general layouts and information architecture.</p>",
     "[[MEDIA:image|Blockframe concepts]]"),
    ("h1-doctor-profile", "My Process",
     "outlined in the full case study presentation.</p>",
     "[[MEDIA:image|High-fidelity profile layout]]"
     "[[MEDIA:image|Lefthand column in focus]]"
     "[[MEDIA:image|Lefthand column iterations]]"
     "[[MEDIA:image|Sticky header options]]"
     "[[MEDIA:image|Final profile design]]"),

    # ------------------------ Egencia Self-Service ------------------------
    ("egencia-self-service", "Background",
     "Executives challenged our team to reduce service calls, the highest operating expense in the company ($150M/year). </p>",
     "[[MEDIA:image|Call propensity — ~50% call rate]]"),
    ("egencia-self-service", "Background",
     "<strong id=\"\">The Bulk Arranger:</strong> booking company events (e.g. offsites)</li></ul>",
     "[[MEDIA:image|Egencia traveler personas]]"),
    ("egencia-self-service", "Background",
     "<li id=\"\"><strong id=\"\">Influence vertical product teams</strong></li></ol>",
     "[[MEDIA:image|Six bets prioritized]]"),
    ("egencia-self-service", "My Process",
     "tested competitor products. </p>",
     "[[MEDIA:image|Competitor audit (Expedia, Airbnb, Dropbox, Wealthfront)]][[MEDIA:image|Airbnb contextual help inspiration]]"),
    ("egencia-self-service", "My Process",
     "fosters a collaborative atmosphere since everyone knows it's lower fidelity. </p>",
     "[[MEDIA:image|Blockframe iterations]]"),
    ("egencia-self-service", "My Process",
     "testing three concepts via Usertesting.com. </p>",
     "[[MEDIA:image|Option 1 — Channel Guidance]][[MEDIA:image|Option 2 — Channel Guidance + Trip]][[MEDIA:image|Option 3 — Simple]]"),
    ("egencia-self-service", "My Process",
     "Calls went up by 5.9%. 🧐</p>",
     "[[MEDIA:image|Option 3 launch — calls +5.9%]]"),
    ("egencia-self-service", "My Process",
     "= Reduced button prominence + shown post search</li></ul>",
     "[[MEDIA:image|Variant C results — calls −2.8%]]"),
]


def main():
    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8")))
    fieldnames = list(rows[0].keys())
    rows_by_slug = {r["Slug"]: r for r in rows}

    # Strip existing markers (idempotent re-runs).
    marker_re = re.compile(r"\[\[MEDIA:[^\]]+\]\]")
    for r in rows:
        for k, v in r.items():
            if isinstance(v, str) and "[[MEDIA:" in v:
                r[k] = marker_re.sub("", v)

    missing = []
    inserted = 0
    for slug, field, anchor, marker in INSERTIONS:
        row = rows_by_slug.get(slug)
        if not row:
            missing.append(f"{slug} (no such project)")
            continue
        if anchor in row[field]:
            row[field] = row[field].replace(anchor, anchor + marker, 1)
            inserted += 1
        else:
            missing.append(f"{slug} / {field}: anchor not found → {anchor[:60]}...")
            row[field] = row[field].rstrip() + marker  # fallback

    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"inserted {inserted} markers")
    if missing:
        print(f"\n⚠️  {len(missing)} anchors not found (markers appended to end of field):")
        for m in missing:
            print(f"  - {m}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
