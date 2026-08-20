# bcm-pdf-to-wordpress

Converts a laid-out Backcountry Magazine print article from PDF into a WordPress draft
that matches the house web format.

The workflow is: extract and repair the copy, rebuild it as real Gutenberg blocks,
write the SEO fields, upload the photos, create a draft. You open the draft, read it,
and publish.

## One-time setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Create a WordPress Application Password

This is WordPress's built-in way to give a program access to your account without
handing over your actual password. It is not an API key from Anthropic and it costs
nothing.

1. Log in to `backcountrymagazine.com/wp-admin`
2. Go to **Users → Profile** (or **Users → All Users → your account**)
3. Scroll to **Application Passwords**
4. Under "New Application Password Name" type something you will recognize later —
   `claude-pdf-converter` — and click **Add New Application Password**
5. WordPress shows a password like `abcd EFGH ijkl MNOP qrst UVWX`. **Copy it now.**
   It is displayed exactly once.

The password inherits your account's permissions and nothing more, and you can revoke
it from that same screen at any time without changing your login.

If the Application Passwords section is missing, an administrator has disabled it, or
the site is not being served over HTTPS. It is enabled on backcountrymagazine.com — the
REST API advertises it at `/wp-json/`.

### 3. Set the credentials

```bash
export WP_URL=https://backcountrymagazine.com
export WP_USER=<your wordpress username>
export WP_APP_PASSWORD='abcd EFGH ijkl MNOP qrst UVWX'
```

Keep the quotes — the password contains spaces. Put these in your shell profile
(`~/.zshrc`) so they persist, or in a `.env` file you do not commit.

**Never commit the password.** If one leaks, revoke it on the profile screen and make
a new one.

### 4. Verify

```bash
curl -u "$WP_USER:$WP_APP_PASSWORD" "$WP_URL/wp-json/wp/v2/users/me?_fields=name,roles"
```

Your name and roles come back if it worked. Run this before the first real conversion —
the site runs All In One WP Security, which can lock out an IP after repeated failed
authentication, so it is worth confirming the credentials are right in one deliberate
request rather than discovering it mid-upload.

## Usage

Normally you just hand Claude the PDF and it runs the skill. Manually:

```bash
python3 scripts/extract_pdf.py article.pdf --out ./workspace
# look at workspace/pages/*.png, correct workspace/article.json if needed
# write plan.json
python3 scripts/build_article.py workspace/article.json --plan plan.json --out workspace
open workspace/preview.html
python3 scripts/wp_publish.py workspace/article.json --plan plan.json --out workspace --dry-run
python3 scripts/wp_publish.py workspace/article.json --plan plan.json --out workspace
```

The last command creates a **draft**. Nothing publishes without `--status publish`.

## What is in here

| File | What it does |
|---|---|
| `SKILL.md` | The procedure Claude follows |
| `references/article-format.md` | BCM's web format, reverse-engineered from published posts |
| `references/seo-rules.md` | Excerpt, SEO title, meta description and keyphrase rules |
| `scripts/bcm_text.py` | Repairs text lifted out of a PDF |
| `scripts/extract_pdf.py` | PDF → structured JSON, images, page renders |
| `scripts/build_article.py` | JSON + decisions → Gutenberg block markup |
| `scripts/wp_publish.py` | Uploads photos, creates the draft |

## Installing the skill

For Claude Code to find it, the skill directory needs to live in one of:

- `<repo>/.claude/skills/` — this repo, available when working here
- `~/.claude/skills/` — available in every project on your machine

To use it everywhere:

```bash
cp -r .claude/skills/bcm-pdf-to-wordpress ~/.claude/skills/
```
