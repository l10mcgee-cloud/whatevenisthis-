"""Text repair for copy lifted out of print PDFs.

A PDF stores glyphs and positions, not sentences. Extracting text gives you line
breaks where the column ended, hyphens where a word was split to fit, ligature
glyphs where the typesetter kerned, and straight quotes where the font had curly
ones. Pasting that into WordPress is what produces the mess this skill exists to
avoid.

Order matters in `clean_paragraph`: ligatures before hyphenation (so a split
ligature rejoins), hyphenation before line joining, quotes last (so they see
final word boundaries).
"""

import re
import unicodedata

LIGATURES = {
    "\ufb00": "ff", "\ufb01": "fi", "\ufb02": "fl", "\ufb03": "ffi",
    "\ufb04": "ffl", "\ufb05": "st", "\ufb06": "st",
    "\u0152": "OE", "\u0153": "oe", "\u00c6": "AE", "\u00e6": "ae",
}

# Stripped outright: soft hyphen, zero-width space/non-joiner/joiner, word joiner,
# BOM, and the directional marks that ride along in some exports.
INVISIBLES = dict.fromkeys(map(ord, "\u00ad\u200b\u200c\u200d\u2060\ufeff\u200e\u200f"), None)

# Spaces that should collapse to a plain space: nbsp, en/em/thin/hair/figure spaces,
# and the narrow no-break space used in French-style punctuation.
ODD_SPACES = dict.fromkeys(
    map(ord, "\u00a0\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u202f\u205f\u3000"),
    " ",
)

PRINT_END_MARKS = "\u220e\u25a0\u25aa\u25fc\u2022"
WEB_END_MARK = "\u2746"  # HEAVY CHEVRON SNOWFLAKE, verified against live posts

# Words that take a leading elision apostrophe rather than an opening quote.
# '80s and 'em are the cases a naive straight-to-curly pass reverses.
ELISIONS = (
    "em", "til", "till", "tis", "twas", "round", "cause", "bout", "nother",
    "n", "ol", "im", "er", "sup", "kay",
)


def strip_invisibles(text):
    return text.translate(INVISIBLES)


def normalize_spaces(text):
    """Collapse exotic space characters, then runs of spaces."""
    text = text.translate(ODD_SPACES)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text


def fix_ligatures(text):
    for glyph, plain in LIGATURES.items():
        text = text.replace(glyph, plain)
    return text


def dehyphenate(text):
    """Rejoin words a typesetter split across a line break.

    Only joins when the break looks typographic: lowercase letter, hyphen, end of
    line, lowercase letter. A hyphen followed by a capital is a real compound that
    happened to land at a line end (`Anti-\\nGravity`), and hyphens inside a line
    are left alone entirely.
    """
    text = re.sub(r"(\w)-\n(\w)", lambda m: m.group(1) + m.group(2)
                  if m.group(2).islower() else m.group(0), text)
    # Some exports use a soft hyphen plus newline, or hyphen plus spaces plus newline.
    text = re.sub(r"(\w)-[ \t]*\n[ \t]*([a-z])", r"\1\2", text)
    # A real compound that happened to break at the line end keeps its hyphen but
    # must close up, or join_lines leaves "Anti- Gravity".
    text = re.sub(r"(\w)-[ \t]*\n[ \t]*([A-Z])", r"\1-\2", text)
    return text


def join_lines(text):
    """Turn visual line breaks into flowing prose, keeping paragraph breaks.

    A blank line is a paragraph break and survives. A single newline is where the
    column ran out and becomes a space.
    """
    text = re.sub(r"\n{2,}", "\x00", text)   # park real paragraph breaks
    text = re.sub(r"[ \t]*\n[ \t]*", " ", text)
    text = text.replace("\x00", "\n\n")
    return text


def fix_dashes(text):
    """Double hyphen to em dash; spaced hyphen between numbers to en dash."""
    text = re.sub(r"(?<!-)--(?!-)", "\u2014", text)
    text = re.sub(r"(\d)\s*-\s*(\d)", "\\1\u2013\\2", text)
    # An em dash with spaces around it is a print convention; BCM sets it tight.
    text = re.sub(r"\s*\u2014\s*", "\u2014", text)
    return text


def curl_quotes(text):
    """Straight quotes to typographic quotes, with elision awareness."""
    # Double quotes: opening when preceded by start/space/open bracket/dash.
    text = re.sub(r'(^|[\s(\[{\u2014\u2013])"', "\\1\u201c", text)
    text = text.replace('"', "\u201d")

    # Leading elisions before the general pass, so '80s and 'em come out right.
    for word in ELISIONS:
        text = re.sub(r"(^|[\s(\[\u2014\u2013])'(%s\b)" % word,
                      "\\1\u2019\\2", text, flags=re.IGNORECASE)
    text = re.sub(r"(^|[\s(\[\u2014\u2013])'(\d0s\b)", "\\1\u2019\\2", text)
    text = re.sub(r"(^|[\s(\[\u2014\u2013])'(\d\d\b)", "\\1\u2019\\2", text)

    # Possessives and contractions: apostrophe between or after word characters.
    text = re.sub(r"(\w)'(\w)", "\\1\u2019\\2", text)
    text = re.sub(r"(\w)'(?=\s|$|[.,;:!?\)\]\u201d])", "\\1\u2019", text)

    # Whatever is left and opens is an opening single quote.
    text = re.sub(r"(^|[\s(\[{\u2014\u2013])'", "\\1\u2018", text)
    text = text.replace("'", "\u2019")
    return text


def fix_punctuation_spacing(text):
    # Ellipsis first: otherwise the space-after-punctuation rule fires inside it.
    text = re.sub(r"\.\s?\.\s?\.", "\u2026", text)
    text = re.sub(r"\s+([.,;:!?%])", r"\1", text)
    text = re.sub(r"([.,;:!?])(?=[A-Za-z\u201c\u2018])", r"\1 ", text)
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\s+\)", ")", text)
    return text


def convert_end_mark(text):
    """Print end marks become the web snowflake."""
    for mark in PRINT_END_MARKS:
        text = text.replace(mark, WEB_END_MARK)
    text = re.sub(r"\s*%s\s*$" % WEB_END_MARK, " " + WEB_END_MARK, text)
    return text


def clean_paragraph(text, end_mark=False):
    """Full repair pass over one paragraph of extracted text."""
    text = unicodedata.normalize("NFC", text)
    text = strip_invisibles(text)
    text = fix_ligatures(text)
    text = dehyphenate(text)
    text = join_lines(text)
    text = normalize_spaces(text)
    text = fix_dashes(text)
    text = fix_punctuation_spacing(text)
    text = curl_quotes(text)
    if end_mark:
        text = convert_end_mark(text)
    else:
        for mark in PRINT_END_MARKS + WEB_END_MARK:
            text = text.replace(mark, "")
    return text.strip()


def strip_furniture(pages_text, min_repeats=None):
    """Remove running heads and folios by finding lines repeated across pages.

    Furniture is text that appears in the same margin band on page after page. The
    signal is repetition: a line that shows up on most pages of a section is a
    running head, not copy. Pure numbers in the first or last two lines of a page
    are folios and go regardless of repetition.
    """
    if min_repeats is None:
        min_repeats = max(2, len(pages_text) // 2)

    counts = {}
    for page in pages_text:
        lines = [ln.strip() for ln in page.splitlines() if ln.strip()]
        for line in set(lines[:3] + lines[-3:]):
            counts[line] = counts.get(line, 0) + 1

    repeated = {ln for ln, n in counts.items() if n >= min_repeats and len(ln) < 80}

    cleaned = []
    for page in pages_text:
        lines = page.splitlines()
        keep = []
        for i, line in enumerate(lines):
            stripped = line.strip()
            near_edge = i < 2 or i >= len(lines) - 2
            if not stripped:
                keep.append(line)
                continue
            if stripped in repeated:
                continue
            if near_edge and re.fullmatch(r"\d{1,3}", stripped):
                continue
            # "27 / Gear Test Week" style section markers.
            if near_edge and re.fullmatch(r"\d{1,3}\s*[/|]\s*.{2,40}", stripped):
                continue
            keep.append(line)
        cleaned.append("\n".join(keep))
    return cleaned


def split_paragraphs(text):
    return [p for p in re.split(r"\n\s*\n", text) if p.strip()]


# Credits trail the caption: "Caption sentence. Liam McGee" or just "Liam McGee".
# The variants below all appear in print.
CREDIT_PREFIX = re.compile(
    r"^\s*(photos?|images?|photography|illustrations?)\s*(by|:)\s*", re.IGNORECASE)


def _looks_like_name(fragment):
    """A short run of capitalized words with no terminal punctuation."""
    frag = fragment.strip().rstrip(".")
    if not frag or len(frag) > 60:
        return False
    words = frag.split()
    if not 1 <= len(words) <= 6:
        return False
    capped = 0
    for w in words:
        core = w.strip("'’.,").replace("-", "")
        if not core:
            continue
        if core.isupper() or (core[:1].isupper() and core[1:].islower()) or core[:1].isupper():
            capped += 1
    # Lowercase connectors are fine inside an org name ("Teton County Search and Rescue").
    return capped >= max(1, len(words) - 2)


def split_caption_credit(text):
    """Separate a figcaption's caption sentence from its trailing photo credit.

    Returns (caption_or_None, credit_or_None). BCM sets the credit as the last
    element of the figcaption, bolded, so it has to come off the caption text
    before the block is built.
    """
    text = (text or "").strip()
    if not text:
        return None, None

    # Explicit label anywhere: "Photo by X" / "Photos: X".
    m = re.search(r"(photos?|images?|photography|illustrations?)\s*(by|:)\s*(.+)$",
                  text, re.IGNORECASE)
    if m:
        caption = text[:m.start()].strip().rstrip("—-– ").strip()
        credit = m.group(3).strip().rstrip(".")
        return (caption or None), (credit or None)

    # No sentence punctuation at all and it reads like a name: credit only.
    if "." not in text.rstrip(".") and _looks_like_name(text):
        return None, text.rstrip(".")

    # Otherwise look for a name fragment after the final sentence period.
    parts = re.split(r"(?<=[.!?”])\s+", text)
    if len(parts) >= 2 and _looks_like_name(parts[-1]):
        credit = parts[-1].strip().rstrip(".")
        caption = " ".join(parts[:-1]).strip()
        return (caption or None), (credit or None)

    return text, None
