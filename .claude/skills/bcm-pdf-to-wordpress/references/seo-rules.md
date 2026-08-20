# SEO fields for BCM articles

Three Yoast fields are writable through the WordPress REST API as post meta.
They are registered on the `posts` endpoint and confirmed present in the schema:

| Field | Meta key |
|---|---|
| SEO title | `_yoast_wpseo_title` |
| Meta description | `_yoast_wpseo_metadesc` |
| Focus keyphrase | `_yoast_wpseo_focuskw` |

Set them in the same `POST /wp/v2/posts` call that creates the draft, inside `meta`.
No separate request, no Yoast-specific endpoint.

---

## Excerpt — copy the dek

The excerpt is **the dek, verbatim**. Do not rewrite it, do not trim it, do not
strip its italics-worth of personality into something flatter. Copy it.

The dek is the first block of the article: a single italic paragraph before the
lead image. Take its text content, drop the `<em>` wrapper, keep the wording exactly.

This is the one SEO-adjacent field that is a copy operation. The other three are
written.

---

## SEO title — replace an atmospheric hed, keep a searchable one

The print hed and the SEO title are different jobs. The hed earns a reader who is
already holding the magazine. The SEO title has to win someone who is typing a
question into Google and has never heard of the story.

So the test is not length. The test is: **would this title find its own article?**

Keep the hed when it already names the subject:

- `Mount Hood Summer Solstice` — keeps. Names the mountain and the occasion.
- `Guillaume "Gee" Pierrel is Killed in Avalanche on K6` — keeps. Names the person,
  the event and the peak. 52 characters, and every one of them is working.
- `Lessons from Alaska: A Photo Diary` — keeps. Names the place and the form.

Replace the hed when it is evocative but opaque:

- `A Quiet Place` → `Backcountry Skiing Patagonia's Undeveloped Aysén`
- `Mountain Skills: Mountain Rescue` → `Alpine Search and Rescue`

Note what the replacements do. They are not keyword mush — they read like a person
wrote them, and they name the thing the piece is actually about. The Patagonia title
carries the activity, the region and the specific valley. The rescue title drops the
department label, which means nothing to a stranger, and keeps the subject.

Rules:

- **60 characters, hard ceiling.** Yoast truncates past that. Observed range is 24–52;
  aim inside it rather than at the edge.
- **Front-load the subject.** The searchable words go first, before any colon or clause.
- **Do not append the magazine name.** The site template handles that.
- **Never change a name, a peak, a date or a fact** to make a title shorter.
- Department labels (`Mountain Skills:`, `Ski Test:`) are print furniture. Drop them from
  the SEO title unless the department name is itself the search term.

When you replace a hed, say so in the summary and show both, so the swap is a decision
Liam sees rather than one he discovers later.

---

## Meta description — written, not copied

Written in Liam's voice. The dek is a starting point for what the piece is about, not
a string to paste. Read `cowrite/references/voice-guide.md` before writing one.

What carries over from the voice guide:

- **AP style.** No serial comma.
- **No em dashes.** They are rationed in his prose and there is no room for one here.
- **No lists.** "x, y and z" in natural language.
- **Understatement over sell.** No "stunning," no "must-read," no "everything you need
  to know." He does not write ad copy and the meta description should not read like it.
- **Concrete over abstract.** Name the mountain, the person, the season, the number.
  "Professional rescuers share when and how to call search and rescue" works because
  every word is load-bearing.

Mechanics:

- **120–156 characters.** Yoast's green range. Observed posts run 67–148; the short end
  is fine when the sentence is genuinely complete, but do not pad to reach 120 and do
  not run past 156.
- **Front-load the keyphrase**, naturally. `Backcountry skiing Patagonia's Cerro Castillo
  introduces a gnawing question` puts the search terms first and still reads like a sentence.
- **Do not restate the hed.** The title is already on the results page. The description
  earns the click by adding what the title could not fit.
- **A question can close it** when the piece is genuinely asking one. It should be the
  article's real question, pulled from the dek or the nut graf, not a manufactured hook.
- **No end mark.** The `❆` belongs on the last graf of the story, nowhere else.

---

## Focus keyphrase — the phrase a reader would actually type

`_yoast_wpseo_focuskw` takes one phrase. Not a comma-separated pile, not a list of
variants. One.

Write it the way Liam would name the piece out loud, which is also, usually, the way
someone would search for it. Two to five words. Lowercase unless it contains a proper
noun.

- `backcountry skiing patagonia`
- `alpine search and rescue`
- `mount hood summer solstice`

Requirements:

- The phrase must **appear in the meta description**, and should appear in the SEO title.
  That is how Yoast scores it, and it is also just a sign the phrase is honest.
- **Name the subject, not the genre.** `backcountry skiing` alone is too broad to rank
  and describes half the archive.
- **No stuffing, no boilerplate.** Do not bolt "backcountry magazine" onto the end.

---

## What to show Liam before publishing

The draft summary lists all four, with character counts on the two that have ceilings:

```
Excerpt        (copied from dek)
SEO title      [N chars]   — flag when it differs from the hed, and show the hed
Meta desc      [N chars]
Focus keyphrase
```

He edits any of them in WP admin before publishing. Nothing here is final, but nothing
here should need fixing either.
