#!/usr/bin/env python3
"""Generate work detail pages from data/work.csv using detail_work.html as template."""

import csv
import json
import re
import shutil
import urllib.parse
from pathlib import Path
from bs4 import BeautifulSoup
from ftfy import fix_text


def img(path: str) -> str:
    """URL-encode a local image path so spaces / special chars survive in HTML."""
    return urllib.parse.quote(path, safe="/")


# Resolved media: when a marker's label appears here, the build script renders
# the real image/embed instead of the dashed placeholder card. Add entries as
# screenshots and embeds come in.
VIMEO_MYSTERY = """<div style="padding:41.88% 0 0 0;position:relative;"><iframe src="https://player.vimeo.com/video/391423749?badge=0&amp;autopause=0&amp;player_id=0&amp;app_id=58479" frameborder="0" allow="autoplay; fullscreen; picture-in-picture; clipboard-write; encrypted-media; web-share" referrerpolicy="strict-origin-when-cross-origin" style="position:absolute;top:0;left:0;width:100%;height:100%;" title="Mystery, because you like doing things."></iframe></div>"""

FIGMA_MYSTERY_FILE = """<iframe style="border:1px solid rgba(0,0,0,0.1);max-width:100%;" width="800" height="450" src="https://www.figma.com/embed?embed_host=share&url=https%3A%2F%2Fwww.figma.com%2Ffile%2FbS0Bepr8E0OQS8qZHS4YNz%2FOnboarding%3Fnode-id%3D1037%253A4781%26t%3DVevgW2WOvrOCZqVz-1" allowfullscreen></iframe>"""

FIGMA_MYSTERY_PROTO = """<iframe style="border:1px solid rgba(0,0,0,0.1);max-width:100%;" width="900" height="900" src="https://www.figma.com/embed?embed_host=share&url=https%3A%2F%2Fwww.figma.com%2Fproto%2FbS0Bepr8E0OQS8qZHS4YNz%2FOnboarding%3Fpage-id%3D3%253A0%26node-id%3D3%253A1354%26viewport%3D1274%252C845%252C0.13%26scaling%3Dscale-down%26starting-point-node-id%3D3%253A1354" allowfullscreen></iframe>"""

FIGMA_H1_FILE = """<iframe style="border:1px solid rgba(0,0,0,0.1);max-width:100%;" width="800" height="450" src="https://www.figma.com/embed?embed_host=share&url=https%3A%2F%2Fwww.figma.com%2Ffile%2F9ugshiThjIteu2kGiE02dd%2F%25F0%259F%25A7%25AD-H1-Explorer%3Fnode-id%3D115%253A87404%26t%3Dkw7RGb4D8oDm4Erm-1" allowfullscreen></iframe>"""

FIGMA_H1_TOFU = """<iframe style="border:1px solid rgba(0,0,0,0.1);max-width:100%;" width="800" height="450" src="https://www.figma.com/embed?embed_host=share&url=https%3A%2F%2Fwww.figma.com%2Ffile%2F9ugshiThjIteu2kGiE02dd%2F%25F0%259F%25A7%25AD-H1-Explorer%3Fnode-id%3D115%253A87039%26t%3Dkw7RGb4D8oDm4Erm-1" allowfullscreen></iframe>"""

FIGMA_H1_LANDING = """<iframe style="border:1px solid rgba(0,0,0,0.1);max-width:100%;" width="800" height="450" src="https://www.figma.com/embed?embed_host=share&url=https%3A%2F%2Fwww.figma.com%2Ffile%2F9ugshiThjIteu2kGiE02dd%2F%25F0%259F%25A7%25AD-H1-Explorer%3Fnode-id%3D122%253A89340%26t%3Dkw7RGb4D8oDm4Erm-1" allowfullscreen></iframe>"""

FIGMA_MERCURY_FF_MULTIVARIANT = """<iframe style="border:1px solid rgba(0,0,0,0.1);max-width:100%;" width="800" height="450" src="https://embed.figma.com/design/q5W8eWBweQ5HHK8cp8BeTy/Focused-Funding?node-id=2015-69245&embed-host=share" allowfullscreen></iframe>"""

FIGMA_MERCURY_FF_FINAL = """<iframe style="border:1px solid rgba(0,0,0,0.1);max-width:100%;" width="800" height="450" src="https://embed.figma.com/proto/q5W8eWBweQ5HHK8cp8BeTy/Focused-Funding?node-id=2-46296&p=f&viewport=-96%2C-18%2C0.19&scaling=min-zoom&content-scaling=fixed&starting-point-node-id=2%3A46296&page-id=0%3A1&embed-host=share" allowfullscreen></iframe>"""

FIGMA_MERCURY_FF_THRESHOLD = """<iframe style="border:1px solid rgba(0,0,0,0.1);max-width:100%;" width="800" height="450" src="https://embed.figma.com/design/q5W8eWBweQ5HHK8cp8BeTy/Focused-Funding?node-id=2015-80225&embed-host=share" allowfullscreen></iframe>"""

FIGMA_MERCURY_VIRAL_SUCCESS_ALTS = """<iframe style="border:1px solid rgba(0,0,0,0.1);max-width:100%;" width="800" height="450" src="https://embed.figma.com/design/knLHsLs6kfXGzX05kcXVz6/Mini-Projects-2025?node-id=63-208284&embed-host=share" allowfullscreen></iframe>"""

FIGMA_MERCURY_FF_MODAL_EXPLORATIONS = """<iframe style="border:1px solid rgba(0,0,0,0.1);max-width:100%;" width="800" height="450" src="https://embed.figma.com/design/q5W8eWBweQ5HHK8cp8BeTy/Focused-Funding?node-id=2025-104647&embed-host=share" allowfullscreen></iframe>"""

MEDIA_RESOLUTIONS = {
    # ---- Mystery Onboarding ----
    "Mystery promo": {"embed": VIMEO_MYSTERY, "responsive": True},
    "Onboarding flow (Figma)": {"embed": FIGMA_MYSTERY_FILE, "aspect": "landscape"},
    "Final onboarding prototype (Figma)": {"embed": FIGMA_MYSTERY_PROTO, "aspect": "square"},
    "Lyft Concierge ride-flow screenshot": {"src": img("images/work/mystery_lyft concierge.png")},
    "Account-creation UX audit screens": {"src": img("images/work/Mystery - Acct creation.png")},
    "Suggested account-creation flow": {"src": img("images/work/Mystery O - Suggestion Acct Creation.png")},
    "Profile enrichment moved to end-of-flow": {"src": img("images/work/Mystery O - Switch.png")},
    # ---- Egencia Onboarding ----
    "Call volume by country": {"src": img("images/work/Egencia Problem.png")},
    "Egencia traveler personas": {"src": img("images/work/Egencia Personas.png")},
    "Strategy considerations (4 lenses)": {"src": img("images/work/Egencia SS Strategy considerations.png")},
    "Team charters + feature bets": {"src": img("images/work/Egencia SS Charters.png")},
    "Value × Effort prioritization": {"src": img("images/work/Egencia SS - Strategy.png")},
    "Help-center variants A/B/C": {
        "srcs": [
            img("images/work/Egencia SS Option 1.png"),
            img("images/work/Egencia SS Option 2.png"),
            img("images/work/Egencia SS Option 3.png"),
        ],
        "caption": "Help-center variants: Option 1, 2, 3",
    },
    "Multivariant test results": {"src": img("images/work/Egencia SS - option 3 variant C results.png")},
    # ---- H1 Browser Extension ----
    "Customer discovery interview (Dartmouth)": {"src": img("images/work/h1 browser - customer discovery interview.png")},
    "Fake Door landing page test": {"src": img("images/work/H1 browser - Fake Door.png")},
    "H1 Explorer (Figma)": {"embed": FIGMA_H1_FILE, "aspect": "landscape"},
    "Top-of-funnel onboarding tab (Figma)": {"embed": FIGMA_H1_TOFU, "aspect": "landscape"},
    "Rate-limit / paywall design": {"src": img("images/work/H1 browser extension - Paywall.png")},
    "Landing-page hero variants (Figma)": {"embed": FIGMA_H1_LANDING, "aspect": "landscape"},
    # ---- H1 Doctor Profile ----
    "H1 platform overview": {"src": img("images/work/H1 Intro image.png")},
    "MSL value-prop diagram": {"src": img("images/work/H1 Value Prop.png")},
    "Legacy profile UX audit issues": {"src": img("images/work/H1 profile -UX issues with legacy.png")},
    "Customer discovery interview": {"src": img("images/work/H1 customer discovery interview.png")},
    "Competitor audit (LinkedIn, Pitchbook, etc.)": {"src": img("images/work/H1 Profile - Audit.png")},
    "Card-sorting design studio (Miro)": {"src": img("images/work/H1 Profile - Card sorting.png")},
    "Blockframe concepts": {"src": img("images/work/H1 Profile - Blockframes.png")},
    "High-fidelity profile layout": {"src": img("images/work/H1 Profile - High fidelity.png")},
    "Lefthand column in focus": {"src": img("images/work/H1 Profile - lefthand colum in focus.png")},
    "Lefthand column iterations": {"src": img("images/work/H1 Profile - left iterations.png")},
    "Sticky header options": {"src": img("images/work/H1 Profile - sticky header.png")},
    "Final profile design": {"src": img("images/work/H1 Profile - final.png")},
    # ---- Egencia Self-Service ----
    "Call propensity (~50% call rate)": {"src": img("images/work/Egencia SS call propensity.png")},
    "Six bets prioritized": {"src": img("images/work/Egencia SS - Strategy.png")},
    "Competitor audit (Expedia, Airbnb, Dropbox, Wealthfront)": {"src": img("images/work/Egencia competitor Audit.png")},
    "Airbnb contextual help inspiration": {"src": img("images/work/Egencia SS - Airbnb inspo.png")},
    "Blockframe iterations": {"src": img("images/work/Egencia SS - blockframe.png")},
    "Option 1: Channel Guidance": {"src": img("images/work/Egencia SS Option 1.png")},
    "Option 2: Channel Guidance + Trip": {"src": img("images/work/Egencia SS Option 2.png")},
    "Option 3: Simple": {"src": img("images/work/Egencia SS Option 3.png")},
    "Option 3 launch (calls +5.9%)": {"src": img("images/work/Egencia SS - option 3 results.png")},
    "Variant C results (calls −2.8%)": {"src": img("images/work/Egencia SS - option 3 variant C results.png")},
    # ---- Mercury Focused Funding ----
    "Focused Funding v1 initial flow": None,  # No screenshot yet; falls back to placeholder card
    "Multivariant test: control vs. 2 funding methods vs. 2 methods + invoicing": {
        "embed": FIGMA_MERCURY_FF_MULTIVARIANT, "aspect": "landscape",
        "caption": "Multivariant: control vs. 2 funding methods vs. 2 methods + invoicing",
    },
    "Final shipped prototype (clickable)": {
        "embed": FIGMA_MERCURY_FF_FINAL, "aspect": "landscape",
        "caption": "Final shipped prototype (click through the flow)",
    },
    "Funding-amount threshold multivariant": {
        "embed": FIGMA_MERCURY_FF_THRESHOLD, "aspect": "landscape",
        "caption": "Fast-follow threshold multivariant test (+$1,500 median deposit)",
    },
    "Modal explorations: takeover vs. embedded": {
        "embed": FIGMA_MERCURY_FF_MODAL_EXPLORATIONS, "aspect": "landscape",
        "caption": "Modal explorations: full takeover vs. embedded with dashboard teaser",
    },
    # ---- Mercury Viral Upsell ----
    "Email value-prop refresh (before and after)": {
        "src": img("images/work/Virality case study - inline - email.png"),
        "caption": "Notification email — value-prop intro added",
    },
    "Landing page rebrand and mobile-responsive refresh": {
        "src": img("images/work/Virality case study - inline - form.png"),
        "caption": "Landing page — rebrand, refreshed container, mobile-responsive",
    },
    "Success screen alternative explorations": {
        "embed": FIGMA_MERCURY_VIRAL_SUCCESS_ALTS, "aspect": "landscape",
        "caption": "Alternatives explored via internal feedback + lightweight user testing",
    },
    "Success screen redesign with value props": {
        "src": img("images/work/Virality case study - inline - success.png"),
        "caption": "Success screen — restated brand, clearer hierarchy, surfaced value props",
    },
    "Success transactional email redesign": {
        "src": img("images/work/Virality case study - inline - success transactional email.png"),
        "caption": "Confirmation email — prominent primary CTA + secondary demo.mercury.com action",
    },
}

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data" / "work.csv"
TEMPLATE_PATH = ROOT / "detail_work.html"
OUTPUT_ROOT = ROOT / "work"
JSON_PATH = ROOT / "data" / "work.json"

# Asset folders referenced by relative paths in the template.
ASSET_PREFIXES = ("css/", "js/", "images/", "documents/")
# Sibling top-level HTML files that the nav and footer link to. From a generated
# case study page at work/<slug>/index.html, these need a "../../" prefix.
SIBLING_PAGES = ("advisory.html", "coaching.html", "content.html",
                 "styleguide.html", "401.html", "404.html",
                 "detail_writing.html", "detail_category.html")

# Inline [[MEDIA:type|label|url?]] markers are inserted into the CSV's rich-text fields
# via scripts/inject_media_markers.py. They render as visible placeholder cards where
# screenshots/embeds need to be re-uploaded.

MEDIA_MARKER_RE = re.compile(r"\[\[MEDIA:(image|figma|video)\|([^|\]]+?)(?:\|([^\]]+))?\]\]")

# Legacy aggregated manifest, no longer rendered, kept here only for reference.
MEDIA_MANIFEST = {
    "mystery-onboarding": [
        {"section": "Background", "type": "video", "label": "Mystery promo (Vimeo embed)", "url": "https://vimeo.com/391423749"},
        {"section": "Background", "type": "image", "label": "Lyft Concierge ride-flow screenshot"},
        {"section": "My Process", "type": "image", "label": "Account-creation UX audit screens"},
        {"section": "My Process", "type": "image", "label": "Suggested account-creation flow"},
        {"section": "My Process", "type": "image", "label": "Profile enrichment moved to end-of-flow"},
        {"section": "My Process", "type": "figma", "label": "Onboarding prototype (Figma embed)"},
    ],
    "egencia-onboarding": [
        {"section": "Background", "type": "image", "label": "Call volume by country (problem framing)"},
        {"section": "Background", "type": "image", "label": "Egencia traveler personas"},
        {"section": "Background", "type": "image", "label": "Strategy considerations (4 lenses)"},
        {"section": "Background", "type": "image", "label": "Team charters + feature bets"},
        {"section": "Background", "type": "image", "label": "Value × Effort prioritization matrix"},
        {"section": "My Process", "type": "image", "label": "Help-center variants A/B/C"},
        {"section": "My Process", "type": "image", "label": "Multivariant test results"},
    ],
    "h1-browser-extension": [
        {"section": "My Process", "type": "image", "label": "Customer discovery interview (Dartmouth)"},
        {"section": "My Process", "type": "image", "label": "Fake Door landing page test"},
        {"section": "My Process", "type": "figma", "label": "H1 Explorer Figma file"},
        {"section": "My Process", "type": "figma", "label": "Top-of-funnel onboarding tab (Figma)"},
        {"section": "My Process", "type": "image", "label": "Rate-limit / paywall design"},
        {"section": "My Process", "type": "figma", "label": "Landing-page hero variants (Figma)"},
    ],
    "h1-doctor-profile": [
        {"section": "Background", "type": "image", "label": "H1 platform overview"},
        {"section": "Background", "type": "image", "label": "MSL value-prop diagram"},
        {"section": "Background", "type": "image", "label": "Legacy profile UX audit issues"},
        {"section": "My Process", "type": "image", "label": "Customer discovery interview"},
        {"section": "My Process", "type": "image", "label": "Competitor audit (LinkedIn, Pitchbook, etc.)"},
        {"section": "My Process", "type": "image", "label": "Card-sorting design studio (Miro)"},
        {"section": "My Process", "type": "image", "label": "Blockframe concepts"},
        {"section": "My Process", "type": "image", "label": "High-fidelity profile layout"},
        {"section": "My Process", "type": "image", "label": "Lefthand column iterations"},
        {"section": "My Process", "type": "image", "label": "Sticky header options"},
        {"section": "My Process", "type": "image", "label": "Final profile design"},
    ],
    "egencia-self-service": [
        {"section": "Background", "type": "image", "label": "Call propensity (50% of travelers call)"},
        {"section": "Background", "type": "image", "label": "Egencia traveler personas"},
        {"section": "My Process", "type": "image", "label": "Competitor audit (Expedia, Airbnb, Dropbox, Wealthfront)"},
        {"section": "My Process", "type": "image", "label": "Airbnb contextual help inspiration"},
        {"section": "My Process", "type": "image", "label": "Blockframe iterations"},
        {"section": "My Process", "type": "image", "label": "Option 1: Channel Guidance"},
        {"section": "My Process", "type": "image", "label": "Option 2: Channel Guidance + Trip info"},
        {"section": "My Process", "type": "image", "label": "Option 3: Simple"},
        {"section": "My Process", "type": "image", "label": "Option 3 launch (call volume +5.9%)"},
        {"section": "My Process", "type": "image", "label": "Variant C multivariant results"},
    ],
}

TYPE_ICONS = {"image": "🖼️", "figma": "🎨", "video": "🎬"}
TYPE_LABELS = {"image": "Screenshot", "figma": "Figma embed", "video": "Video embed"}

PLACEHOLDER_STYLE = """
<style>
.media-placeholder-inline { display:flex; align-items:center; gap:0.75rem; background:#FAFAFA; border:1px dashed #C9C9C9; border-radius:8px; padding:1rem 1.25rem; margin:1.5rem 0; font-family:inherit; }
.media-placeholder-inline__icon { font-size:1.25rem; flex-shrink:0; }
.media-placeholder-inline__body { flex:1; min-width:0; }
.media-placeholder-inline__type { font-size:0.7rem; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color:#888; margin:0 0 0.15rem; }
.media-placeholder-inline__label { font-size:0.95rem; color:#222; margin:0; }
.media-placeholder-inline__link { display:block; font-size:0.8rem; color:#666; margin-top:0.25rem; word-break:break-all; }

/* Widen the Background / My Process / My Learnings content-wrappers to span
   the full 12-column grid, then constrain text width inside so reading lines
   stay comfortable while figures span the full body container.
   The Webflow IDs below are the Background/Process/Learnings grid children. */
#w-node-_8e7a808a-05f1-28fb-7746-2e79cb1c0a37-a59cf88f,
#w-node-e7e06211-75c3-8fac-fd90-6842c36c5c69-a59cf88f,
#w-node-_6dfeafc6-d375-0552-3f07-a31eaac38e2d-a59cf88f {
  grid-area: 1 / 1 / 2 / -1 !important;
}

/* Constrain reading width for text inside the now-wider content-wrappers. */
#w-node-_8e7a808a-05f1-28fb-7746-2e79cb1c0a37-a59cf88f > h2,
#w-node-e7e06211-75c3-8fac-fd90-6842c36c5c69-a59cf88f > h2,
#w-node-_6dfeafc6-d375-0552-3f07-a31eaac38e2d-a59cf88f > h2,
#w-node-_8e7a808a-05f1-28fb-7746-2e79cb1c0a37-a59cf88f > .padding-top,
#w-node-e7e06211-75c3-8fac-fd90-6842c36c5c69-a59cf88f > .padding-top,
#w-node-_6dfeafc6-d375-0552-3f07-a31eaac38e2d-a59cf88f > .padding-top {
  max-width: 52rem;
  margin-left: auto;
  margin-right: auto;
  width: 100%;
}
.w-richtext > *:not(figure) {
  max-width: 52rem;
  margin-left: auto;
  margin-right: auto;
}

/* Figures span the full content-wrapper width (now == container-large). */
.w-richtext figure.rich-media-figure {
  width: 100%;
  max-width: 100%;
  margin: 2.5rem 0;
}
.w-richtext figure.rich-media-figure img {
  display: block;
  width: 100%;
  height: auto;
  border-radius: 4px;
}
.w-richtext figure.rich-media-figure iframe {
  display: block;
  width: 100%;
  border: 1px solid rgba(0,0,0,0.1);
  background: #f5f5f5;
}
.w-richtext figure.rich-media-figure.is-iframe-landscape iframe { aspect-ratio: 16 / 9; height: auto; }
.w-richtext figure.rich-media-figure.is-iframe-square iframe { aspect-ratio: 1 / 1; height: auto; }
.w-richtext figure.rich-media-figure.is-responsive-video > div { width: 100%; }
.w-richtext figure.rich-media-figure.is-image-stack { display: flex; flex-direction: column; gap: 1.5rem; }
/* Extra-wide variant: break past the .container-large 80rem cap and span the
   full viewport (minus a bit of breathing room). Useful for embeds with
   built-in chrome that needs more horizontal real estate to read. */
.w-richtext figure.rich-media-figure.is-extra-wide {
  width: 100vw;
  max-width: 100vw;
  margin-left: calc(50% - 50vw);
  margin-right: calc(50% - 50vw);
}
@media (max-width: 991px) {
  .w-richtext figure.rich-media-figure.is-extra-wide {
    width: calc(100vw - 4rem);
    margin-left: calc(50% - 50vw + 2rem);
    margin-right: calc(50% - 50vw + 2rem);
  }
}
.w-richtext figure.rich-media-figure figcaption { font-size: 0.85rem; color: #666; margin-top: 0.75rem; text-align: center; }
</style>
"""


def render_media_marker(match: "re.Match") -> str:
    mtype, label, url = match.group(1), match.group(2).strip(), (match.group(3) or "").strip()

    resolution = MEDIA_RESOLUTIONS.get(label)
    if resolution:
        caption = resolution.get("caption", label)
        if "srcs" in resolution:
            imgs = "".join(
                f'<img src="{s}" alt="{caption}" loading="lazy">' for s in resolution["srcs"]
            )
            return f'<figure class="rich-media-figure is-image-stack">{imgs}<figcaption>{caption}</figcaption></figure>'
        if "src" in resolution:
            return (
                f'<figure class="rich-media-figure">'
                f'<img src="{resolution["src"]}" alt="{caption}" loading="lazy">'
                f'<figcaption>{caption}</figcaption></figure>'
            )
        if "embed" in resolution:
            classes = ["rich-media-figure"]
            if resolution.get("responsive"):
                classes.append("is-responsive-video")
            aspect = resolution.get("aspect")
            if aspect == "landscape":
                classes.append("is-iframe-landscape")
            elif aspect == "square":
                classes.append("is-iframe-square")
            if resolution.get("width") == "extra-wide":
                classes.append("is-extra-wide")
            return f'<figure class="{" ".join(classes)}">{resolution["embed"]}<figcaption>{caption}</figcaption></figure>'

    # Fall through; still unresolved, render the dashed placeholder.
    icon = TYPE_ICONS.get(mtype, "📎")
    type_label = TYPE_LABELS.get(mtype, mtype.title())
    link_html = (
        f'<a class="media-placeholder-inline__link" href="{url}" target="_blank" rel="noopener">{url}</a>'
        if url else ""
    )
    return (
        f'<div class="media-placeholder-inline">'
        f'<span class="media-placeholder-inline__icon">{icon}</span>'
        f'<div class="media-placeholder-inline__body">'
        f'<p class="media-placeholder-inline__type">{type_label} · to re-import</p>'
        f'<p class="media-placeholder-inline__label">{label}</p>'
        f"{link_html}"
        f"</div></div>"
    )


def fix_asset_paths(soup: BeautifulSoup) -> None:
    """Rewrite relative asset and page paths to be relative to work/<slug>/index.html (2 levels up)."""
    for tag in soup.find_all(True):
        for attr in ("href", "src"):
            val = tag.get(attr)
            if not isinstance(val, str):
                continue
            if val.startswith(ASSET_PREFIXES):
                tag[attr] = "../../" + val
            elif val == "index.html" or val.startswith("index.html#") or val.startswith("index.html?"):
                tag[attr] = "../../" + val
            elif val in SIBLING_PAGES or val.split("#", 1)[0].split("?", 1)[0] in SIBLING_PAGES:
                tag[attr] = "../../" + val


def set_inner_html(tag, html: str) -> None:
    tag.clear()
    fixed = MEDIA_MARKER_RE.sub(render_media_marker, fix_text(html))
    fragment = BeautifulSoup(fixed, "html.parser")
    for child in list(fragment.children):
        tag.append(child)


def build_media_placeholder(slug: str, soup: BeautifulSoup):
    items = MEDIA_MANIFEST.get(slug, [])
    if not items:
        return None
    from collections import defaultdict
    by_section = defaultdict(list)
    for it in items:
        by_section[it["section"]].append(it)

    html = [PLACEHOLDER_STYLE, '<div class="media-placeholder">']
    html.append('<p class="media-placeholder__title">Media to re-import</p>')
    html.append(
        '<p class="media-placeholder__note">These screenshots, Figma embeds, and videos lived inside the original '
        f'<a href="https://scottchristensen.design/work/{slug}/" target="_blank" rel="noopener">'
        f'live case study</a> but weren\'t in the Webflow CMS export. Re-export and drop them back in once available.</p>'
    )
    for section, group in by_section.items():
        html.append(f'<div class="media-placeholder__group"><p class="media-placeholder__group-title">{section}</p>')
        for it in group:
            icon = TYPE_ICONS.get(it["type"], "📎")
            link = f' <span class="media-placeholder__link">{it["url"]}</span>' if it.get("url") else ""
            html.append(
                f'<div class="media-placeholder__item"><span class="media-placeholder__icon">{icon}</span>'
                f'<span>{it["label"]}{link}</span></div>'
            )
        html.append("</div>")
    html.append("</div>")
    return BeautifulSoup("".join(html), "html.parser")


def strip_empty_class(tag) -> None:
    if not tag:
        return
    classes = tag.get("class", [])
    tag["class"] = [c for c in classes if c not in ("w-dyn-bind-empty",)]


def find_rich_text_after_heading(soup, heading_text: str):
    for h2 in soup.find_all("h2"):
        if h2.get_text(strip=True) == heading_text:
            section = h2.find_parent("section")
            if section:
                return section.find("div", class_="text-rich-text")
    return None


def build_page(row: dict, slug_to_title: dict) -> str:
    soup = BeautifulSoup(TEMPLATE_PATH.read_text(encoding="utf-8"), "html.parser")

    title = row["Grid title"].strip()

    # <title>
    if soup.title:
        soup.title.string = f"{title} · Scott Christensen ·"

    # Page heading (h1) and breadcrumb leaf
    h1 = soup.select_one("h1.heading-xlarge.w-dyn-bind-empty")
    if h1:
        h1.string = title
        strip_empty_class(h1)

    breadcrumb_leaf = soup.select_one(".breadcrumb_item .text-color-grey.text-style-1line")
    if breadcrumb_leaf:
        breadcrumb_leaf.string = title
        strip_empty_class(breadcrumb_leaf)

    # Overview (first text-rich-text after the Overview heading h2... but this template's first
    # rich-text sits inside .project-details-container before any h2 in a section).
    project_details = soup.select_one(".project-details-container")
    if project_details:
        overview_div = project_details.find("div", class_="text-rich-text")
        if overview_div:
            set_inner_html(overview_div, row["Overview"])
            strip_empty_class(overview_div)

    # Button (text + href + arrow direction)
    button = soup.select_one(".project-details-container a.button")
    if button:
        link = row["Button link"] or "#"
        button["href"] = link
        if link.startswith("http"):
            button["target"] = "_blank"
            button["rel"] = "noopener"
        elif button.has_attr("target"):
            del button["target"]
        btn_text_div = button.select_one(".button-wrapper > .w-dyn-bind-empty")
        if btn_text_div:
            btn_text_div.string = row["Button text"] or "Learn more"
            strip_empty_class(btn_text_div)
        # Swap arrow direction for in-page anchor links
        arrow_div = button.select_one(".button-wrapper > div:last-child")
        if arrow_div and link.startswith("#"):
            arrow_div.string = " ↓"

    # Role / Team / Duration (3 .project-details paragraphs inside .content-wrapper.is-project-details)
    details_wrapper = soup.select_one(".content-wrapper.is-project-details")
    if details_wrapper:
        paragraphs = details_wrapper.select(".project-details p")
        values = [row["My role"], row["The team"], row["Year / Duration"]]
        for p, val in zip(paragraphs, values):
            # Preserve newlines as <br>
            p.clear()
            parts = (val or "").split("\n")
            for i, part in enumerate(parts):
                if i > 0:
                    p.append(soup.new_tag("br"))
                p.append(part)
            strip_empty_class(p)

    # Full-bleed image (first collection-list-wrapper, .project-image-full-bleed)
    full_bleed_img = soup.select_one("img.project-image-full-bleed")
    if full_bleed_img:
        if row["Full bleed image"]:
            full_bleed_img["src"] = row["Full bleed image"]
            full_bleed_img["alt"] = f"{title} (full bleed)"
            # White phone mockup on white bg blends in; give it a subtle bottom edge.
            if row["Slug"] == "mercury-focused-funding":
                full_bleed_img["style"] = "border-bottom: 1px solid #e5e5e5;"
            wrapper = full_bleed_img.find_parent("div", class_="collection-list-wrapper")
            empty = wrapper.find("div", class_="w-dyn-empty") if wrapper else None
            if empty:
                empty.decompose()
        else:
            section = full_bleed_img.find_parent("figure") or full_bleed_img.find_parent("section")
            if section:
                section.decompose()

    # Remove the empty extra image sections (CSV has no data for these fields).
    for img in soup.select("img.project-image.is-2-col, img.project-image"):
        section = img.find_parent("section")
        if section:
            section.decompose()

    # Background / My Process / My Learnings rich text
    bg = find_rich_text_after_heading(soup, "Background")
    if bg and row["Background"]:
        set_inner_html(bg, row["Background"])
        strip_empty_class(bg)
        bg_section = bg.find_parent("section")
        if bg_section and not bg_section.get("id"):
            bg_section["id"] = "background"
    elif bg:
        bg.find_parent("section").decompose()

    proc = find_rich_text_after_heading(soup, "My Process")
    if proc and row["My Process"]:
        set_inner_html(proc, row["My Process"])
        strip_empty_class(proc)
    elif proc:
        proc.find_parent("section").decompose()

    learn = find_rich_text_after_heading(soup, "My Learnings")
    if learn and row["Learnings"]:
        set_inner_html(learn, row["Learnings"])
        strip_empty_class(learn)
    elif learn:
        learn.find_parent("section").decompose()

    # Inject the inline-placeholder stylesheet once into <head>.
    if soup.head and not soup.find("style", string=lambda s: s and "media-placeholder-inline" in s):
        style_fragment = BeautifulSoup(PLACEHOLDER_STYLE, "html.parser")
        for child in list(style_fragment.children):
            soup.head.append(child)

    # Next project
    next_slug = row["Next project"].strip()
    if next_slug:
        next_link = soup.select_one("a.is-next-project-link")
        if next_link:
            next_link["href"] = f"../{next_slug}/"
            next_h3 = next_link.select_one("h3.heading-xlarge.w-dyn-bind-empty")
            if next_h3:
                next_h3.string = slug_to_title.get(next_slug, next_slug)
                strip_empty_class(next_h3)

    # Update the work nav links and homepage links to use the absolute hash anchor on this site.
    for a in soup.find_all("a"):
        href = a.get("href", "")
        if href == "https://www.scottchristensen.design/#work":
            a["href"] = "../../index.html#work"
        elif href == "https://www.scottchristensen.design/#about":
            a["href"] = "../../index.html#about"

    fix_asset_paths(soup)

    return str(soup)


def main():
    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8")))
    # Defensive: repair any mojibake (double-encoded emoji/curly quotes) in every field.
    for r in rows:
        for k, v in r.items():
            if isinstance(v, str):
                r[k] = fix_text(v)
    visible = [r for r in rows if r["Hide"].strip().lower() != "true"]

    # Map every project (including hidden) for next-project resolution.
    slug_to_title = {r["Slug"]: r["Grid title"] for r in rows}

    # Clear and recreate output directory.
    if OUTPUT_ROOT.exists():
        shutil.rmtree(OUTPUT_ROOT)
    OUTPUT_ROOT.mkdir(parents=True)

    for row in rows:
        # Build pages for all rows, even Hide=true, so internal "next" links resolve.
        slug = row["Slug"]
        out_dir = OUTPUT_ROOT / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        html = build_page(row, slug_to_title)
        (out_dir / "index.html").write_text(html, encoding="utf-8")
        print(f"  wrote work/{slug}/index.html")

    # Also refresh data/work.json for the homepage script (visible projects only).
    # featured_slug = "" → no featured project; js/work.js hides the empty wrapper.
    featured_slug = ""
    featured = []
    grid = []
    for r in sorted(visible, key=lambda r: int(r["Order"]), reverse=True):
        item = {
            "slug": r["Slug"],
            "title": r["Grid title"],
            "subtitle": r["Grid description"],
            "image": r["Grid Image"],
        }
        if r["Slug"] == featured_slug:
            featured.append(item)
        else:
            grid.append(item)

    JSON_PATH.write_text(json.dumps({"featured": featured, "grid": grid}, indent=2), encoding="utf-8")
    print(f"  wrote data/work.json ({len(featured)} featured, {len(grid)} grid)")


if __name__ == "__main__":
    main()
