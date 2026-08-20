#!/usr/bin/env python3
"""Pull structured content out of a laid-out Backcountry Magazine PDF.

Writes a workspace containing the extracted article as JSON, every embedded image
as a web-ready file, and a PNG render of every page.

    python3 extract_pdf.py article.pdf --out ./workspace

The classifier is a set of typographic heuristics: the hed is the biggest type on
the opening page, the dek is the italic run under it, subheads are short bold
lines at body size, captions are the small type near images. Heuristics on a
magazine layout are right most of the time and confidently wrong the rest, which
is why the page renders exist. Confirm every classification against the render
before building the article.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bcm_text  # noqa: E402


def load_pymupdf():
    try:
        import pymupdf
        return pymupdf
    except ImportError:
        pass
    try:
        import fitz
        return fitz
    except ImportError:
        pass
    print("Installing PyMuPDF...", file=sys.stderr)
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "PyMuPDF"])
    import pymupdf
    return pymupdf


BOLD_FLAG = 1 << 4
ITALIC_FLAG = 1 << 1


def span_style(span):
    flags = span.get("flags", 0)
    font = span.get("font", "").lower()
    return {
        "bold": bool(flags & BOLD_FLAG) or "bold" in font or "black" in font
                or "heavy" in font or "semibold" in font,
        "italic": bool(flags & ITALIC_FLAG) or "italic" in font or "oblique" in font,
        "font": span.get("font", ""),
        "size": round(span.get("size", 0), 1),
    }


def line_text(line):
    return "".join(s.get("text", "") for s in line.get("spans", []))


def collect_lines(page):
    """Every text line on the page with its geometry and dominant style."""
    out = []
    data = page.get_text("dict")
    for block in data.get("blocks", []):
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            spans = line.get("spans", [])
            if not spans:
                continue
            text = line_text(line)
            if not text.strip():
                continue
            # Dominant style = the style of the longest span in the line.
            lead = max(spans, key=lambda s: len(s.get("text", "")))
            style = span_style(lead)
            x0, y0, x1, y1 = line["bbox"]
            out.append({
                "text": text,
                "x0": round(x0, 1), "y0": round(y0, 1),
                "x1": round(x1, 1), "y1": round(y1, 1),
                "block": block.get("number", 0),
                "all_bold": all(span_style(s)["bold"] for s in spans if s.get("text", "").strip()),
                "all_italic": all(span_style(s)["italic"] for s in spans if s.get("text", "").strip()),
                **style,
            })
    return out


def detect_columns(lines, page_width, tolerance=0.06):
    """Cluster line left-edges into columns.

    Magazine body copy sits in columns and PyMuPDF's natural block order can run a
    spread's columns together. Clustering left edges recovers the intended reading
    order for the common case of evenly-set columns.
    """
    if not lines:
        return []
    edges = sorted(ln["x0"] for ln in lines)
    gap = page_width * tolerance
    clusters = [[edges[0]]]
    for e in edges[1:]:
        if e - clusters[-1][-1] <= gap:
            clusters[-1].append(e)
        else:
            clusters.append([e])
    # Keep clusters with enough lines to be a real column.
    return [sum(c) / len(c) for c in clusters if len(c) >= 3]


def reading_order(lines, page_width):
    """Sort lines into reading order, column-aware when columns are detectable."""
    cols = detect_columns(lines, page_width)
    if len(cols) < 2:
        return sorted(lines, key=lambda l: (l["y0"], l["x0"]))

    def column_of(line):
        return min(range(len(cols)), key=lambda i: abs(line["x0"] - cols[i]))

    return sorted(lines, key=lambda l: (column_of(l), l["y0"], l["x0"]))


def body_size(all_lines):
    """Most common line size weighted by character count."""
    counts = Counter()
    for ln in all_lines:
        counts[ln["size"]] += len(ln["text"])
    return counts.most_common(1)[0][0] if counts else 10.0


BYLINE_RE = re.compile(
    r"^\s*((?:words?|story|text|photos?|images?|photography)"
    r"(?:\s*(?:&|and|\+|,)\s*(?:words?|story|text|photos?|images?|photography))*)"
    r"\s+(by|:)\s*(.+)$"
    r"|^\s*by\s+(.+)$",
    re.IGNORECASE,
)


def parse_byline(text):
    """Read a byline off a line, or return None.

    The bare `by NAME` form has to be held to a name test. Magazine copy is set
    justified and wraps anywhere, so a body line beginning "by land area in the
    world..." matches the pattern perfectly and is not a byline. A labelled form
    ("words & photos by X") is unambiguous enough to trust on its own.
    """
    m = BYLINE_RE.match(text.strip())
    if not m:
        return None
    if m.group(3):
        kind = m.group(1).lower()
        who = m.group(3)
        labelled = True
    else:
        kind = "words"
        who = m.group(4)
        labelled = False
    who = bcm_text.clean_paragraph(who).strip(" .,")
    if not labelled and not bcm_text._looks_like_name(who):
        return None
    role = "photos" if kind.startswith(("photo", "image")) else "words"
    return {"role": role, "name": who}


def classify(lines, body_pt, page_index, page_rect):
    """Label each line by typographic role."""
    page_h = page_rect[3] - page_rect[1]
    max_size = max((ln["size"] for ln in lines), default=body_pt)

    for ln in lines:
        size = ln["size"]
        text = ln["text"].strip()
        rel_y = (ln["y0"] - page_rect[1]) / page_h if page_h else 0.5

        folio_like = (re.fullmatch(r"\d{1,3}", text)
                      or re.fullmatch(r"\d{1,3}\s*[/|]\s*.{2,40}", text))
        byline = parse_byline(text)
        if (rel_y < 0.06 or rel_y > 0.94) and folio_like:
            ln["role"] = "furniture"
        elif byline:
            ln["role"] = "byline"
            ln["byline"] = byline
        elif page_index == 0 and size >= max(max_size * 0.8, body_pt * 1.8):
            ln["role"] = "hed"
        elif ln["all_italic"] and size > body_pt * 1.05:
            ln["role"] = "dek"
        elif size >= body_pt * 1.4 and len(text) > 12:
            # Display type well above body size is a pull quote or display line.
            # The length floor only keeps stray large glyphs (a drop cap, a folio
            # set big) out; it must stay well under a short pull-quote line.
            ln["role"] = "pullquote"
        elif size <= body_pt * 0.88:
            ln["role"] = "caption"
        elif ln["all_bold"] and len(text) < 60 and not text.endswith((".", "?", "!")):
            ln["role"] = "subhead"
        elif (rel_y < 0.05 or rel_y > 0.95) and len(text) < 40:
            ln["role"] = "furniture"
        else:
            ln["role"] = "body"
    return lines


def group_runs(lines):
    """Merge consecutive lines that share a role into single text runs."""
    runs = []
    for ln in lines:
        if runs and runs[-1]["role"] == ln["role"] and ln["role"] in ("body", "dek", "caption", "pullquote", "hed"):
            # A vertical jump larger than a line and a half is a new paragraph.
            prev = runs[-1]
            if ln["y0"] - prev["y1"] > ln["size"] * 0.9 and ln["role"] == "body":
                runs.append({"role": ln["role"], "text": ln["text"],
                             "y0": ln["y0"], "y1": ln["y1"], "lines": [ln]})
                continue
            # An indent also starts a paragraph.
            if ln["role"] == "body" and ln["x0"] - min(l["x0"] for l in prev["lines"]) > 6:
                runs.append({"role": ln["role"], "text": ln["text"],
                             "y0": ln["y0"], "y1": ln["y1"], "lines": [ln]})
                continue
            prev["text"] += "\n" + ln["text"]
            prev["y1"] = ln["y1"]
            prev["lines"].append(ln)
        else:
            runs.append({"role": ln["role"], "text": ln["text"],
                         "y0": ln["y0"], "y1": ln["y1"], "lines": [ln],
                         **({"byline": ln["byline"]} if "byline" in ln else {})})
    return runs


SENTENCE_END = ".!?\u2746"


def ends_a_paragraph(text):
    """True when text reads as a finished paragraph.

    A paragraph that runs past the bottom of a column continues in the next one,
    so the last character is the tell: a sentence-final mark ends a paragraph, and
    anything else — a comma, a hyphen, a bare word — means the sentence is still
    going. Closing quotes and brackets are transparent; what matters is what sits
    under them.
    """
    stripped = (text or "").rstrip()
    while stripped and stripped[-1] in "\u201d\u2019\")]":
        stripped = stripped[:-1].rstrip()
    return bool(stripped) and stripped[-1] in SENTENCE_END


def merge_continuations(blocks):
    """Rejoin body paragraphs split across a column or page break."""
    merged = []
    for block in blocks:
        if (merged and merged[-1]["type"] == "body" and block["type"] == "body"
                and not ends_a_paragraph(merged[-1]["text"])):
            prev = merged[-1]
            if prev["text"].rstrip().endswith("-"):
                prev["text"] = prev["text"].rstrip()[:-1] + block["text"].lstrip()
            else:
                prev["text"] = prev["text"].rstrip() + " " + block["text"].lstrip()
            continue
        merged.append(block)
    return merged


def extract_images(pymupdf, doc, outdir, min_px=200):
    """Save every embedded raster, converting CMYK and alpha to RGB JPEG."""
    imgdir = os.path.join(outdir, "images")
    os.makedirs(imgdir, exist_ok=True)
    found = []
    seen = set()
    for pno in range(len(doc)):
        page = doc[pno]
        for info in page.get_images(full=True):
            xref = info[0]
            if xref in seen:
                continue
            seen.add(xref)
            try:
                pix = pymupdf.Pixmap(doc, xref)
            except Exception as exc:
                print(f"  ! xref {xref}: {exc}", file=sys.stderr)
                continue
            if pix.width < min_px or pix.height < min_px:
                continue
            # CMYK (and any alpha) has to become RGB before it is web-usable.
            if pix.n - pix.alpha >= 4 or pix.alpha:
                pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
            name = f"img-{len(found) + 1:03d}.jpg"
            path = os.path.join(imgdir, name)
            pix.save(path, jpg_quality=92)
            rects = page.get_image_rects(xref)
            bbox = [round(v, 1) for v in rects[0]] if rects else None
            found.append({
                "file": os.path.join("images", name),
                "page": pno + 1,
                "width": pix.width,
                "height": pix.height,
                "bbox": bbox,
                "caption": None,
                "credit": None,
                "alt": None,
            })
    return found


def attach_captions(images, page_runs):
    """Pair each image with the nearest caption run below it on the same page."""
    for img in images:
        if not img["bbox"]:
            continue
        runs = page_runs.get(img["page"], [])
        candidates = [r for r in runs if r["role"] == "caption" and r["y0"] >= img["bbox"][3] - 4]
        if not candidates:
            candidates = [r for r in runs if r["role"] == "caption"]
        if not candidates:
            continue
        best = min(candidates, key=lambda r: abs(r["y0"] - img["bbox"][3]))
        text = bcm_text.clean_paragraph(best["text"])
        img["caption"], img["credit"] = bcm_text.split_caption_credit(text)
        best["used"] = True
    return images


def render_pages(doc, outdir, dpi):
    pagedir = os.path.join(outdir, "pages")
    os.makedirs(pagedir, exist_ok=True)
    zoom = dpi / 72.0
    import pymupdf as _pm
    mat = _pm.Matrix(zoom, zoom)
    paths = []
    for i, page in enumerate(doc):
        pix = page.get_pixmap(matrix=mat)
        p = os.path.join(pagedir, f"p-{i + 1:03d}.png")
        pix.save(p)
        paths.append(p)
    return paths


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf")
    ap.add_argument("--out", default="./workspace")
    ap.add_argument("--dpi", type=int, default=150)
    ap.add_argument("--no-images", action="store_true",
                    help="skip embedded-image extraction (use when supplying real photo files)")
    ap.add_argument("--no-render", action="store_true")
    args = ap.parse_args()

    pymupdf = load_pymupdf()
    doc = pymupdf.open(args.pdf)
    os.makedirs(args.out, exist_ok=True)
    rawdir = os.path.join(args.out, "raw")
    os.makedirs(rawdir, exist_ok=True)

    # Pass one: gather every line so body size is measured across the whole piece.
    per_page = []
    for pno, page in enumerate(doc):
        lines = collect_lines(page)
        lines = reading_order(lines, page.rect.width)
        per_page.append((pno, page, lines))

    all_lines = [ln for _, _, lines in per_page for ln in lines]
    if not all_lines:
        print("No extractable text. This PDF is probably scanned or outlined; "
              "it needs OCR before it can be converted.", file=sys.stderr)
        return 1
    body_pt = body_size(all_lines)

    page_runs = {}
    raw_pages = []
    for pno, page, lines in per_page:
        rect = [page.rect.x0, page.rect.y0, page.rect.x1, page.rect.y1]
        classify(lines, body_pt, pno, rect)
        runs = group_runs(lines)
        page_runs[pno + 1] = runs
        raw = "\n".join(ln["text"] for ln in lines)
        raw_pages.append(raw)

    raw_pages = bcm_text.strip_furniture(raw_pages)
    for i, raw in enumerate(raw_pages):
        with open(os.path.join(rawdir, f"p{i + 1:03d}.txt"), "w") as fh:
            fh.write(raw)

    images = [] if args.no_images else extract_images(pymupdf, doc, args.out)
    if images:
        attach_captions(images, page_runs)

    # Assemble the article in page then reading order.
    hed, dek, bylines, blocks = [], [], [], []
    for pno in sorted(page_runs):
        for run in page_runs[pno]:
            role = run["role"]
            if role == "furniture" or run.get("used"):
                continue
            if role == "hed":
                hed.append(run["text"])
            elif role == "dek":
                dek.append(run["text"])
            elif role == "byline":
                bylines.append(run["byline"])
            elif role in ("body", "subhead", "pullquote", "caption"):
                # Keep any end mark for now. Stripping here would delete the one
                # the last paragraph needs before there is any way to know which
                # paragraph is last.
                blocks.append({"type": role, "page": pno,
                               "text": bcm_text.clean_paragraph(run["text"],
                                                                end_mark=True)})

    article = {
        "source_pdf": os.path.abspath(args.pdf),
        "pages": len(doc),
        "body_point_size": body_pt,
        "hed": bcm_text.clean_paragraph(" ".join(hed)) if hed else None,
        "dek": bcm_text.clean_paragraph(" ".join(dek)) if dek else None,
        "bylines": bylines,
        "blocks": blocks,
        "images": images,
    }

    article["blocks"] = merge_continuations(article["blocks"])

    # The end mark belongs on the last body block and nowhere else.
    body_blocks = [b for b in article["blocks"] if b["type"] == "body"]
    for block in body_blocks[:-1]:
        for mark in bcm_text.PRINT_END_MARKS + bcm_text.WEB_END_MARK:
            block["text"] = block["text"].replace(mark, "")
        block["text"] = block["text"].strip()
    if body_blocks:
        last = body_blocks[-1]
        last["text"] = bcm_text.convert_end_mark(last["text"])
        last["is_last"] = True

    with open(os.path.join(args.out, "article.json"), "w") as fh:
        json.dump(article, fh, indent=2, ensure_ascii=False)

    if not args.no_render:
        render_pages(doc, args.out, args.dpi)

    counts = Counter(b["type"] for b in article["blocks"])
    print(f"Wrote {args.out}/article.json")
    print(f"  {len(doc)} pages, body type {body_pt}pt")
    print(f"  hed: {article['hed'] or '(none found)'}")
    print(f"  dek: {(article['dek'] or '(none found)')[:80]}")
    print(f"  bylines: {article['bylines'] or '(none found)'}")
    print(f"  blocks: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    print(f"  images: {len(images)}")
    print()
    print("Now look at the page renders and confirm these before building.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
