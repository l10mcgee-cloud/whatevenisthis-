---
name: bcm-pdf-to-wordpress
description: >
  Convert a laid-out Backcountry Magazine print article from PDF into a WordPress draft
  that matches BCM's house web format and is ready to publish. Use this skill whenever
  Liam points to a PDF of a print story and wants it online, posted, put on the site,
  built in WordPress or "turned into a web article." Trigger on: "convert this PDF,"
  "put this on the site," "build this in WordPress," "make this a web article," "post
  this story," "get this online," "turn this into a post," or any PDF handed over
  alongside a folder of photos and an issue number. It extracts and repairs the copy,
  rebuilds it as real Gutenberg blocks in BCM's format, writes the SEO fields in Liam's
  voice, uploads the photos and creates a draft. For proofing a laid-out PDF before it
  goes to press, use bcm-pdf-proof instead. For proofing raw manuscripts, use proofreader.
---

# BCM PDF to WordPress

A print article and a web article are the same story in two different machines. The PDF
holds glyphs at coordinates; WordPress holds blocks in a database. Copying between them
by hand is where the formatting damage happens — the hyphens that were line breaks, the
quotes that went straight, the drop cap that became a normal letter, the credit that
lost its bold.

This skill does the mechanical conversion so that the only thing left is judgment.

Two rules govern everything below.

**The format is not a choice.** BCM's web format is fixed and documented in
`references/article-format.md`, read out of published posts. Do not improvise it, do not
improve it, do not substitute `<h2>` for a bold subhead because that would be better SEO.
Match the house pattern.

**The scripts measure; you judge.** The extractor guesses at structure from type sizes
and it is confidently wrong often enough that you must check its work against the page
renders. Everything that requires taste — which hed is atmospheric, where the lede-in
bold should break, what the photo actually shows — is yours.

---

## Before you start

You need, at minimum, the PDF. You should also ask for, if they were not offered:

- **The real photo files.** Images embedded in a print PDF are CMYK, cropped to the
  print trim, and sometimes broken into fragments by the layout. The extractor pulls
  them and converts them to RGB so there is always something, but a folder of the
  actual photos design used is meaningfully better. Ask once; do not block on it.
- **The issue number and name**, and the shop URL for that issue. Without these the
  "originally published in" footer gets skipped.
- **Photo credits**, if they are not legible in the PDF captions.

Do not ask about things you can determine yourself. The article type is usually obvious
from the layout, the byline is in the PDF, and the category is Stories (49) unless the
piece is clearly gear.

---

## Step 1: Extract

```bash
python3 scripts/extract_pdf.py <the-pdf> --out ./workspace
```

Add `--no-images` when Liam supplied the real photo files, so the workspace is not
cluttered with print rasters nobody will use.

This writes:

- `workspace/article.json` — hed, dek, bylines, classified blocks, images with captions
- `workspace/pages/p-NNN.png` — every page rendered
- `workspace/raw/pNNN.txt` — extracted text per page, furniture stripped
- `workspace/images/` — embedded rasters, converted to RGB

The copy in `article.json` has already been through the repair pass in
`scripts/bcm_text.py`: dehyphenated, ligatures expanded, quotes curled, line breaks
joined into paragraphs, print end mark converted. That is the copy-paste damage handled.

---

## Step 2: Look at the pages

**View every page render before you build anything.** This is the step that separates a
good conversion from a plausible one, and it is not optional.

What you are checking:

- **Did the columns come out in reading order?** The extractor clusters lines into
  columns, which handles a standard two- or three-column set. A story that jumps a
  spread, wraps around a photo, or runs in an irregular measure can interleave. Read the
  first sentence of each body block in `article.json` against the page. If the prose
  does not flow, fix the order before continuing.
- **Is the hed right?** It is taken as the largest type on page one, which a section
  opener or a display quote can beat.
- **Is the dek right?** Taken as italic type above body size. A pull quote set in italic
  can be mistaken for one.
- **Which blocks are actually subheads?** Bold and short is the test, and a bold lede-in
  looks identical to a subhead from the type alone.
- **Are captions matched to the right photos?** The extractor pairs a caption to the
  nearest image above it. On a spread with two photos and stacked captions, that is a
  coin flip. Confirm each one against what is in the frame.
- **What is missing?** Sidebars, stat boxes, tester cards and pull quotes are laid out
  as separate elements and may have been classified as body copy or dropped. Decide what
  belongs in the web version.

Fix anything wrong by editing `article.json` directly. It is plain JSON and that is
faster than arguing with the heuristics.

---

## Step 3: Decide the article type

This sets the opening graf treatment, which is the first thing a reader sees.

- **Feature** — bold lede-in on the first three to five words, spacer under the lead
  image, no drop cap.
- **Department or news** — drop cap on the first paragraph, no spacer.

The PDF usually tells you: if the print opening graf has a bolded or small-caps lede-in,
it is a feature. If it opens with a drop cap, it is a department. When the layout is
ambiguous, ask Liam rather than guessing — it is one question and it is visible on the
published page.

For a feature, choose where the bold run ends. Three to five words, breaking at a
phrase boundary, never mid-clause. "**Frozen dirt and shale** cascade down" is right.
"**Frozen dirt and shale cascade**" is not.

---

## Step 4: Write the plan

`plan.json` holds every editorial decision. Write it into the workspace:

```json
{
  "type": "feature",
  "title": "A Quiet Place",
  "status": "draft",
  "categories": [49],
  "coauthors": ["Liam McGee"],
  "issue": {
    "number": 165,
    "name": "The Photo Annual",
    "shop_url": "https://shop.holpublications.com/..."
  },
  "seo": {
    "title": "Backcountry Skiing Patagonia's Undeveloped Aysén",
    "metadesc": "Backcountry skiing Patagonia's Cerro Castillo introduces a gnawing question: Can we protect wild places by actually skiing them?",
    "focuskw": "backcountry skiing patagonia"
  },
  "images": [
    {"source": "/path/to/real-photo.jpg", "lead": true,
     "caption": "Two members of an Alpenglow Expeditions trip take their time on the climb.",
     "credit": "Liam McGee",
     "alt": "Two skiers climbing a wind-scoured ridge under flat afternoon light"},
    {"source": "/path/to/second.jpg", "position": 4,
     "caption": "...", "credit": "...", "alt": "..."}
  ]
}
```

Notes on the fields that are easy to get wrong:

- **`position`** is an index into the body paragraphs. `0` places the image before the
  first paragraph, `4` before the fifth. The lead image is separate and marked `lead`.
- **`source`** is the real photo file. Omit it to use the raster extracted from the PDF.
- **`alt`** is required on every image. Write real alt text describing what is in the
  frame. The hand-built posts all ship `alt=""` and that is a gap worth closing, not a
  pattern worth matching.
- **`coauthors`** sets the byline through Co-Authors Plus. The posts endpoint takes
  author-taxonomy **term ids**, not usernames, so the script resolves names through the
  plugin's authenticated search first. Pass display names (`"Liam McGee"`) or, if you
  already know them, raw term ids. When a name cannot be resolved unambiguously the
  script says so and leaves the byline unset rather than guessing — set it from the
  Authors box in WP admin, which takes a few seconds. Use the real byline from the PDF,
  not the account doing the posting.
- **`title`** is the print hed. The SEO title is separate and often different.

The excerpt is not in the plan because it is never a decision: it is the dek, copied.

---

## Step 5: Write the SEO fields

Read `references/seo-rules.md` and follow it. The short version:

- **Excerpt** — the dek, verbatim. A copy, not a rewrite.
- **SEO title** — keep the print hed when it already names its subject; replace it when
  it is atmospheric. 60 characters hard ceiling.
- **Meta description** — written in Liam's voice, 120 to 156 characters. Read
  `cowrite/references/voice-guide.md` first. AP style, no serial comma, no em dashes, no
  sell. Front-load the keyphrase.
- **Focus keyphrase** — one phrase, two to five words, and it must appear in the meta
  description.

These are the fields most likely to be wrong in a way nobody notices for a month, so
show all four with character counts when you report back.

---

## Step 6: Build and proof

```bash
python3 scripts/build_article.py workspace/article.json --plan plan.json --out workspace
```

Writes `content.html` (the block markup), `post.json` (the REST payload) and
`preview.html` (a readable page for proofing).

**Read `preview.html` before going near WordPress.** Check the opening graf treatment,
that the credits are bold and last in their captions, that the end mark is on the final
paragraph and appears exactly once, that the issue footer names the right issue.

The builder prints warnings for missing alt text, missing credits, a missing or repeated
end mark, unfilled TKs, and SEO fields outside their limits. Resolve them rather than
publishing through them.

---

## Step 7: Create the draft

Dry run first, always:

```bash
python3 scripts/wp_publish.py workspace/article.json --plan plan.json --out workspace --dry-run
```

Then, with credentials set:

```bash
export WP_URL=https://backcountrymagazine.com
export WP_USER=<wordpress username>
export WP_APP_PASSWORD='xxxx xxxx xxxx xxxx xxxx xxxx'
python3 scripts/wp_publish.py workspace/article.json --plan plan.json --out workspace
```

It authenticates, uploads each photo, rebuilds the content with the real attachment ids,
creates the post as a **draft**, and sets the lead image as the featured image.

**Never pass `--status publish` on your own.** The draft is the deliverable. Liam opens
it, reads it, and publishes. Publish only if he asks for it in those words.

Report back with the edit URL, the preview URL, and the four SEO fields with their
character counts. Say plainly what you were unsure about — a caption you could not
verify against its photo, a block you could not classify, a spread you flattened into
single images.

---

## Things this skill does not do

- **It does not rewrite the story.** The copy is edited and proofed already. Repair the
  extraction damage and change nothing else. If a real error survives into the web
  version, mention it; do not silently fix it.
- **It does not rebuild galleries, groups or column layouts.** Print photo essays are
  designed by hand. Place the images in reading order and say the grouping needs a human.
- **It does not publish.** See above.
- **It does not handle scanned or outlined PDFs.** If the extractor reports no
  extractable text, the file needs OCR first and there is no point guessing.
