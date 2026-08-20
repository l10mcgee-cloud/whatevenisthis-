#!/usr/bin/env python3
"""Turn extracted PDF content into Backcountry Magazine block markup.

    python3 build_article.py workspace/article.json --plan plan.json --out workspace

Emits:
    content.html   Gutenberg block markup, ready to POST as the post content
    post.json      the full REST payload for POST /wp/v2/posts
    preview.html   a standalone page for proofing the article before it goes near
                   WordPress

Every block carries its `<!-- wp:... -->` delimiters. Without them WordPress
collapses the whole article into one Classic block, which renders fine and is
miserable to edit. See references/article-format.md.
"""

import argparse
import html
import json
import os
import re
import sys

SUBSCRIBE_URL = "https://backcountrymagazine.com/subscribe/"
END_MARK = "❆"


def esc(text):
    """Escape markup characters, leaving typographic characters as UTF-8."""
    return html.escape(text or "", quote=False)


def esc_attr(text):
    return html.escape(text or "", quote=True)


def p_block(inner, attrs=None, classes=None):
    attr_json = ""
    if attrs:
        attr_json = " " + json.dumps(attrs, separators=(",", ":"), ensure_ascii=False)
    cls = f' class="{classes}"' if classes else ""
    return f"<!-- wp:paragraph{attr_json} -->\n<p{cls}>{inner}</p>\n<!-- /wp:paragraph -->"


def dek_block(dek):
    return p_block(f"<em>{esc(dek)}</em>")


def subhead_block(text):
    return p_block(f"<strong>{esc(text.rstrip('.'))}</strong>")


def body_block(text, drop_cap=False, bold_words=0):
    text = esc(text)
    if bold_words:
        words = text.split()
        n = min(bold_words, len(words))
        text = f"<strong>{' '.join(words[:n])}</strong> {' '.join(words[n:])}".strip()
    if drop_cap:
        return p_block(text, attrs={"dropCap": True}, classes="has-drop-cap")
    return p_block(text)


def image_block(image):
    """An image block. Requires a real attachment id and url once published."""
    media_id = image.get("id")
    url = image.get("url") or image.get("file")
    caption = (image.get("caption") or "").strip()
    credit = (image.get("credit") or "").strip()
    alt = image.get("alt") or ""

    figcap = ""
    if caption or credit:
        pieces = []
        if caption:
            pieces.append(esc(caption))
        if credit:
            pieces.append(f"<strong>{esc(credit)}</strong>")
        figcap = ('<figcaption class="wp-element-caption">'
                  + " ".join(pieces) + "</figcaption>")

    attrs = {"sizeSlug": "large", "linkDestination": "none", "align": "center"}
    img_class = ""
    if media_id:
        attrs = {"id": media_id, **attrs}
        img_class = f' class="wp-image-{media_id}"'

    attr_json = json.dumps(attrs, separators=(",", ":"), ensure_ascii=False)
    return (f"<!-- wp:image {attr_json} -->\n"
            f'<figure class="wp-block-image aligncenter size-large">'
            f'<img src="{esc_attr(url)}" alt="{esc_attr(alt)}"{img_class}/>'
            f"{figcap}</figure>\n"
            f"<!-- /wp:image -->")


def spacer_block(height=56):
    return (f'<!-- wp:spacer {{"height":"{height}px"}} -->\n'
            f'<div style="height:{height}px" aria-hidden="true" class="wp-block-spacer"></div>\n'
            f"<!-- /wp:spacer -->")


def separator_block():
    return ('<!-- wp:separator -->\n'
            '<hr class="wp-block-separator has-alpha-channel-opacity"/>\n'
            '<!-- /wp:separator -->')


def issue_footer_block(issue):
    """The 'originally published in' footer.

    The italics break around the issue name: everything is italic except the issue
    number and name themselves. Anchors carry href and nothing else — the stray
    `id` attributes visible in hand-built posts are copy-paste residue and are
    exactly what this function exists to stop reproducing.
    """
    number = issue.get("number")
    name = (issue.get("name") or "").strip()
    shop_url = issue.get("shop_url") or ""

    label = f"Issue {number}" if number else "this issue"
    if name:
        label += f", {name}"

    grab = (f'<a href="{esc_attr(shop_url)}">grab a copy</a>' if shop_url
            else "grab a copy")
    inner = (
        "<em>This article was originally published in </em>"
        f"{esc(label)}"
        f"<em>. To read, {grab}, or "
        f'<a href="{SUBSCRIBE_URL}">subscribe</a> to read our stories when '
        "they’re first published.</em>"
    )
    return p_block(inner)


def place_images(blocks, images):
    """Interleave image blocks into the body at their requested positions.

    `position` is an index into the body-paragraph sequence: 0 puts the image
    before the first body paragraph. Images without a position land in the order
    they were extracted, after the lead.
    """
    by_pos = {}
    floating = []
    for img in images:
        pos = img.get("position")
        if pos is None:
            floating.append(img)
        else:
            by_pos.setdefault(int(pos), []).append(img)

    out = []
    body_index = 0
    for block in blocks:
        if block["type"] == "body":
            for img in by_pos.get(body_index, []):
                out.append(("image", img))
            body_index += 1
        out.append(("block", block))
    for img in by_pos.get(body_index, []):
        out.append(("image", img))
    for img in floating:
        out.append(("image", img))
    return out


def build(article, plan):
    art_type = plan.get("type", "department")
    dek = plan.get("dek") or article.get("dek")
    blocks = [b for b in article.get("blocks", []) if b["type"] in ("body", "subhead")]

    images = plan.get("images")
    if images is None:
        images = article.get("images", [])

    lead = None
    rest = list(images)
    for i, img in enumerate(rest):
        if img.get("lead"):
            lead = rest.pop(i)
            break
    if lead is None and rest and rest[0].get("position") is None:
        lead = rest.pop(0)

    parts = []
    if dek:
        parts.append(dek_block(dek))
    if lead:
        parts.append(image_block(lead))
    if art_type == "feature":
        parts.append(spacer_block(plan.get("spacer_height", 56)))

    drop_cap = plan.get("drop_cap")
    if drop_cap is None:
        drop_cap = art_type in ("department", "news")
    bold_words = plan.get("lede_bold_words")
    if bold_words is None:
        bold_words = 4 if art_type == "feature" else 0

    first_body_done = False
    for kind, payload in place_images(blocks, rest):
        if kind == "image":
            parts.append(image_block(payload))
            continue
        block = payload
        if block["type"] == "subhead":
            parts.append(subhead_block(block["text"]))
        else:
            text = block["text"]
            if not first_body_done:
                parts.append(body_block(text, drop_cap=drop_cap, bold_words=bold_words))
                first_body_done = True
            else:
                parts.append(body_block(text))

    issue = plan.get("issue")
    if issue:
        parts.append(separator_block())
        parts.append(issue_footer_block(issue))

    return "\n\n".join(parts)


def check(content, article, plan):
    """Warnings worth seeing before this reaches WordPress."""
    problems = []
    marks = content.count(END_MARK)
    if marks == 0:
        problems.append("No end mark. The final body graf should end with a space and ❆.")
    elif marks > 1:
        problems.append(f"End mark appears {marks} times; it belongs on the last graf only.")

    for img in plan.get("images", article.get("images", [])):
        if not img.get("alt"):
            problems.append(f"{img.get('file') or img.get('url')}: no alt text.")
        if not img.get("credit"):
            problems.append(f"{img.get('file') or img.get('url')}: no photo credit.")

    if "TK" in content:
        for m in re.finditer(r".{0,40}\bTK\b.{0,40}", content):
            problems.append(f"Unfilled TK: …{m.group(0).strip()}…")

    if not plan.get("issue"):
        problems.append("No issue info, so the 'originally published in' footer was skipped.")

    seo = plan.get("seo", {})
    title = seo.get("title") or ""
    if len(title) > 60:
        problems.append(f"SEO title is {len(title)} chars; Yoast truncates past 60.")
    desc = seo.get("metadesc") or ""
    if desc and not 120 <= len(desc) <= 156:
        problems.append(f"Meta description is {len(desc)} chars; Yoast's green range is 120-156.")
    kw = seo.get("focuskw") or ""
    if kw and desc and kw.lower() not in desc.lower():
        problems.append(f"Focus keyphrase “{kw}” does not appear in the meta description.")
    return problems


PREVIEW_CSS = """
body{max-width:44rem;margin:3rem auto;padding:0 1.5rem;font:18px/1.65 Georgia,serif;color:#1a1a1a}
figure{margin:2.5rem 0}figure img{width:100%;height:auto}
figcaption{font:italic 14px/1.5 system-ui,sans-serif;color:#666;margin-top:.6rem}
.has-drop-cap:first-letter{float:left;font-size:3.4em;line-height:.85;padding:.05em .1em 0 0;font-weight:700}
hr{border:0;border-top:1px solid #ddd;margin:2.5rem 0}
.note{background:#fff8e1;border-left:3px solid #e0a800;padding:.8rem 1rem;font:14px/1.5 system-ui,sans-serif;margin:0 0 2rem}
"""


def preview(content, article, plan, problems):
    title = plan.get("seo", {}).get("title") or plan.get("title") or article.get("hed") or "Untitled"
    banner = ""
    if problems:
        items = "".join(f"<li>{esc(p)}</li>" for p in problems)
        banner = f'<div class="note"><strong>Before publishing:</strong><ul>{items}</ul></div>'
    body = re.sub(r"<!--.*?-->", "", content)
    return (f"<!doctype html><meta charset=utf-8><title>{esc(title)}</title>"
            f"<style>{PREVIEW_CSS}</style>{banner}<h1>{esc(plan.get('title') or article.get('hed') or '')}</h1>{body}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("article_json")
    ap.add_argument("--plan", help="JSON of editorial decisions (type, seo, images, issue)")
    ap.add_argument("--out", default=".")
    args = ap.parse_args()

    with open(args.article_json) as fh:
        article = json.load(fh)
    plan = {}
    if args.plan and os.path.exists(args.plan):
        with open(args.plan) as fh:
            plan = json.load(fh)

    content = build(article, plan)
    problems = check(content, article, plan)
    os.makedirs(args.out, exist_ok=True)

    with open(os.path.join(args.out, "content.html"), "w") as fh:
        fh.write(content)
    with open(os.path.join(args.out, "preview.html"), "w") as fh:
        fh.write(preview(content, article, plan, problems))

    dek = plan.get("dek") or article.get("dek") or ""
    seo = plan.get("seo", {})
    payload = {
        "title": plan.get("title") or article.get("hed") or "",
        "status": plan.get("status", "draft"),
        "content": content,
        "excerpt": dek,                     # the excerpt is the dek, verbatim
        "categories": plan.get("categories", [49]),
        "tags": plan.get("tags", []),
        "meta": {k: v for k, v in {
            "_yoast_wpseo_title": seo.get("title"),
            "_yoast_wpseo_metadesc": seo.get("metadesc"),
            "_yoast_wpseo_focuskw": seo.get("focuskw"),
        }.items() if v},
    }
    if plan.get("slug"):
        payload["slug"] = plan["slug"]
    if plan.get("coauthors"):
        payload["coauthors"] = plan["coauthors"]

    with open(os.path.join(args.out, "post.json"), "w") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)

    print(f"content.html  {len(content)} chars")
    print(f"post.json     title: {payload['title']!r}")
    print(f"preview.html  open this and read it before publishing")
    if problems:
        print("\nBefore publishing:")
        for p in problems:
            print(f"  - {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
