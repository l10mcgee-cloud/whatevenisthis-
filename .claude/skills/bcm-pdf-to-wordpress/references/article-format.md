# The BCM web article format

Reverse-engineered from live posts on backcountrymagazine.com. Every pattern below was
read out of published markup, not invented.

Reference posts:

- `339169` "Mountain Skills: Mountain Rescue" — department, drop cap
- `339060` "A Quiet Place" — feature, bold lede-in, galleries
- `344793` "Guillaume 'Gee' Pierrel is Killed in Avalanche on K6" — news

---

## Write block markup, not bare HTML

The single most important mechanical rule. WordPress stores Gutenberg blocks as HTML
wrapped in comment delimiters:

```html
<!-- wp:paragraph -->
<p>The wind came up in the afternoon.</p>
<!-- /wp:paragraph -->
```

If you POST bare `<p>` tags with no delimiters, WordPress swallows the whole article into
a single Classic block. It renders fine and it is miserable to edit — no per-paragraph
controls, no image sidebar, and the drop cap toggle is gone. Liam opens the draft to
proof it, so it has to be real blocks.

The `wp-block-paragraph` class visible in rendered output is added by WordPress at render
time. Do not write it into stored content.

---

## Order of blocks

1. **Dek** — one italic paragraph
2. **Lead image** — with credit
3. **Spacer** (features only, 56px)
4. **Body** — opening graf styled per article type, then paragraphs and bold subheads,
   images interleaved
5. **End mark** — `❆` on the final graf
6. **Separator**
7. **Issue footer**

---

## Dek

```html
<!-- wp:paragraph -->
<p><em>Professional rescuers share when and how to call search and rescue.</em></p>
<!-- /wp:paragraph -->
```

Whole thing italic, including terminal punctuation. One paragraph, however long — the
Patagonia dek runs three sentences and stays one block.

This same text, minus the `<em>`, becomes the post excerpt. See `seo-rules.md`.

---

## Images

```html
<!-- wp:image {"id":339171,"sizeSlug":"large","linkDestination":"none","align":"center"} -->
<figure class="wp-block-image aligncenter size-large"><img src="https://backcountrymagazine.com/wp-content/uploads/2026/06/photo.jpg" alt="ALT TEXT" class="wp-image-339171"/><figcaption class="wp-element-caption">Caption sentence. <strong>Photographer Name</strong></figcaption></figure>
<!-- /wp:image -->
```

The `id` in the block attributes and the `wp-image-N` class must both be the real
attachment ID returned by the media upload. A mismatch breaks the block on load.

**The credit is the last thing in the figcaption, wrapped in `<strong>`.** This is
consistent across every post checked. Two shapes:

- Credit only, when the photo needs no explanation:
  `<figcaption class="wp-element-caption"><strong>Teton Country Search and Rescue</strong></figcaption>`
- Caption then credit, separated by a space:
  `<figcaption class="wp-element-caption">Two members of an Alpenglow Expeditions trip take their time on the climb, knowing the descent will be less than perfect. <strong>Liam McGee</strong></figcaption>`

Caption text ends with a period. The credit does not take one.

**Alt text.** Every image checked on recent posts has `alt=""`. Write real alt text —
describe what is in the frame for someone who cannot see it. This is the one place the
skill deliberately improves on the hand-built posts rather than matching them.

---

## The opening graf

Two house patterns, chosen by article type. Getting this wrong is the most visible
formatting error in the whole conversion, because it is the first thing on the page.

**Departments and news — drop cap:**

```html
<!-- wp:paragraph {"dropCap":true} -->
<p class="has-drop-cap">A thin layer of early-season snow painted Washington's Snoqualmie Pass&hellip;</p>
<!-- /wp:paragraph -->
```

**Features — bold lede-in.** The first few words carry `<strong>`, no drop cap:

```html
<!-- wp:paragraph -->
<p><strong>Frozen dirt and shale</strong> cascade down into the gully below with each step.</p>
<!-- /wp:paragraph -->
```

The bolded run is three to five words and breaks at a natural phrase boundary, not
mid-clause. In print this is the design's lede-in treatment, so when the PDF shows a
bolded or small-caps opening run, carry the same word count over.

When the article type is ambiguous, ask rather than guess.

---

## Subheads are bold paragraphs

```html
<!-- wp:paragraph -->
<p><strong>Know your ABCs</strong></p>
<!-- /wp:paragraph -->
```

**Not `<h2>`.** There is not a single heading tag in the articles checked. This is a
real SEO cost and it is not this skill's call to change unilaterally — match the house
pattern and raise it with Liam separately if it comes up.

Sentence case, no terminal punctuation.

---

## Spacer

Features use a spacer between the lead image and the opening graf:

```html
<!-- wp:spacer {"height":"56px"} -->
<div style="height:56px" aria-hidden="true" class="wp-block-spacer"></div>
<!-- /wp:spacer -->
```

---

## End mark

The last paragraph of the story ends with a space and `❆` (U+2744).

```html
<p>&hellip;from your gear choices to your terrain selection to how quickly you call for help. ❆</p>
```

Print uses `∎`. Web uses `❆`. Convert it. The end mark goes on the final body graf,
before the separator, and appears exactly once in the article.

---

## Separator and issue footer

```html
<!-- wp:separator -->
<hr class="wp-block-separator has-alpha-channel-opacity"/>
<!-- /wp:separator -->

<!-- wp:paragraph -->
<p><em>This article was originally published in </em>Issue 165, The Photo Annual<em>. To read, <a href="SHOP_URL">grab a copy</a>, or <a href="https://backcountrymagazine.com/subscribe/">subscribe</a> to read our stories when they're first published.</em></p>
<!-- /wp:paragraph -->
```

Note the italics break around the issue name — "Issue 165, The Photo Annual" is roman,
everything around it is italic. That is deliberate and it is easy to lose.

The subscribe URL is constant. The shop URL is per-issue and has to be supplied.

**This block is why the skill exists.** On post 339169 the shop link points at Issue 165
while carrying a leftover `id` attribute referencing Issue 167 — the fingerprint of a
block hand-copied from the previous article and incompletely updated. Generating it
removes that failure mode. Never copy a stray `id` or `type` attribute into an anchor.

---

## Typography

Print PDFs carry artifacts that have to be cleaned before anything reaches WordPress.
`scripts/bcm_text.py` handles all of this; the list is here so the rules are reviewable.

| Fix | From | To |
|---|---|---|
| Hyphenation at line breaks | `moun-\ntain` | `mountain` |
| Ligatures | `ﬁ ﬂ ﬀ ﬃ ﬄ` | `fi fl ff ffi ffl` |
| Straight quotes | `"` `'` | `"` `"` `'` `'` |
| Double hyphen | `--` | `—` |
| Print end mark | `∎` `■` | `❆` |
| Soft hyphens, zero-width | `U+00AD` `U+200B` | removed |
| Non-breaking space | `U+00A0` | regular space |
| Multiple spaces | `word  word` | `word word` |
| Space before punctuation | `word .` | `word.` |

Apostrophes need direction awareness: `'80s` and `don't` both take `'` (U+2019), while an
opening single quote takes `'`. The elision cases — `'80s`, `'em`, `'til` — are the ones a
naive straight-to-curly pass gets backwards.

**Running heads and folios must be stripped.** Repeated text in the top or bottom band of
every page is furniture, not copy. The Gear Guide running head `27 / Gear Test Week` is a
known trap: the 27 is a section marker, not a page number, and it appears on pages whose
real folio is something else.

---

## Blocks the skill does not generate

Galleries (`wp:gallery`), groups and columns appear in feature layouts. They are laid out
by hand for a reason and the skill does not attempt to reconstruct them from a print
spread. When a PDF spread is clearly a photo essay grid, place the images as individual
image blocks in reading order and note in the summary that the grouping needs a human.
