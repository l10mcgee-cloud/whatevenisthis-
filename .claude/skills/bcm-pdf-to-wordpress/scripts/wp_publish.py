#!/usr/bin/env python3
"""Upload images and create the article draft on WordPress.

    export WP_URL=https://backcountrymagazine.com
    export WP_USER=liam
    export WP_APP_PASSWORD='xxxx xxxx xxxx xxxx xxxx xxxx'

    python3 wp_publish.py workspace/article.json --plan plan.json --out workspace
    python3 wp_publish.py workspace/article.json --plan plan.json --dry-run

Uploads happen before the post is created, because an image block needs the real
attachment id — writing the block first and patching ids in afterward is how you
get blocks that fail validation on load.

Defaults to creating a draft. Publishing takes --status publish and should be a
decision Liam makes, not one this script makes for him.
"""

import argparse
import json
import mimetypes
import os
import sys

try:
    import requests
except ImportError:
    print("pip install requests", file=sys.stderr)
    raise

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_article  # noqa: E402


class WordPress:
    def __init__(self, base, user, app_password):
        self.base = base.rstrip("/") + "/wp-json/wp/v2"
        self.session = requests.Session()
        self.session.auth = (user, app_password)
        self.session.headers["User-Agent"] = "bcm-pdf-to-wordpress"

    def _raise(self, resp, what):
        try:
            detail = resp.json()
            msg = detail.get("message", resp.text[:300])
            code = detail.get("code", "")
        except ValueError:
            msg, code = resp.text[:300], ""
        raise SystemExit(f"{what} failed [{resp.status_code} {code}]: {msg}")

    def whoami(self):
        r = self.session.get(f"{self.base}/users/me", timeout=30)
        if not r.ok:
            self._raise(r, "Authentication")
        return r.json()

    def upload_media(self, path, alt=None, title=None):
        filename = os.path.basename(path)
        ctype = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        with open(path, "rb") as fh:
            data = fh.read()
        r = self.session.post(
            f"{self.base}/media",
            data=data,
            headers={"Content-Disposition": f'attachment; filename="{filename}"',
                     "Content-Type": ctype},
            timeout=180,
        )
        if not r.ok:
            self._raise(r, f"Upload of {filename}")
        media = r.json()

        # alt text is a second call; it is not accepted on the binary upload.
        fields = {}
        if alt:
            fields["alt_text"] = alt
        if title:
            fields["title"] = title
        if fields:
            r2 = self.session.post(f"{self.base}/media/{media['id']}", json=fields, timeout=60)
            if r2.ok:
                media = r2.json()
        return media

    def resolve_coauthors(self, names):
        """Turn byline names into author-taxonomy term ids.

        The `coauthors` field on the posts endpoint takes term ids from the author
        taxonomy that Co-Authors Plus registers, not usernames and not user ids.
        Integers are passed through on the assumption the caller looked them up.
        Names go through the plugin's authenticated search, and because that
        endpoint's response shape is not documented, anything that does not yield
        an unambiguous term id is reported rather than guessed at — a byline set
        to the wrong person is worse than a byline set by hand.
        """
        resolved, unresolved = [], []
        for name in names:
            if isinstance(name, int):
                resolved.append(name)
                continue
            r = self.session.get(f"{self.base.replace('/wp/v2', '')}/coauthors/v1/search",
                                 params={"q": name}, timeout=30)
            if not r.ok:
                unresolved.append(name)
                continue
            try:
                results = r.json()
            except ValueError:
                unresolved.append(name)
                continue
            if isinstance(results, dict):
                results = results.get("results") or results.get("data") or []
            term_id = None
            for item in results if isinstance(results, list) else []:
                if not isinstance(item, dict):
                    continue
                nicename = (item.get("user_nicename") or "").lower()
                display = (item.get("display_name") or "").lower()
                if name.lower() not in (nicename, display):
                    continue
                for key in ("term_id", "termId", "author_term_id"):
                    if isinstance(item.get(key), int):
                        term_id = item[key]
                        break
                if term_id:
                    break
            if term_id:
                resolved.append(term_id)
            else:
                unresolved.append(name)
        return resolved, unresolved

    def create_post(self, payload):
        r = self.session.post(f"{self.base}/posts", json=payload, timeout=120)
        if not r.ok:
            self._raise(r, "Post creation")
        return r.json()

    def update_post(self, post_id, payload):
        r = self.session.post(f"{self.base}/posts/{post_id}", json=payload, timeout=60)
        if not r.ok:
            self._raise(r, f"Post {post_id} update")
        return r.json()


def resolve_image_paths(plan, article, workspace):
    """Choose which file to upload for each image.

    An explicit `source` in the plan wins — that is the real high-res photo from
    design. Otherwise fall back to the raster pulled out of the PDF, which is
    print-cropped and only as good as the export.
    """
    images = plan.get("images")
    if images is None:
        images = [dict(i) for i in article.get("images", [])]
    for img in images:
        src = img.get("source") or img.get("file")
        if src and not os.path.isabs(src):
            candidate = os.path.join(workspace, src)
            img["_path"] = candidate if os.path.exists(candidate) else src
        else:
            img["_path"] = src
    return images


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("article_json")
    ap.add_argument("--plan")
    ap.add_argument("--out", default=None)
    ap.add_argument("--status", default=None, choices=["draft", "publish", "pending", "private"])
    ap.add_argument("--dry-run", action="store_true",
                    help="build and report, upload nothing, create nothing")
    args = ap.parse_args()

    workspace = args.out or os.path.dirname(os.path.abspath(args.article_json))
    with open(args.article_json) as fh:
        article = json.load(fh)
    plan = {}
    if args.plan and os.path.exists(args.plan):
        with open(args.plan) as fh:
            plan = json.load(fh)
    if args.status:
        plan["status"] = args.status

    images = resolve_image_paths(plan, article, workspace)

    missing = [i["_path"] for i in images if not i.get("_path") or not os.path.exists(i["_path"])]
    if missing and not args.dry_run:
        raise SystemExit("Image files not found:\n  " + "\n  ".join(str(m) for m in missing))

    if args.dry_run:
        plan["images"] = images
        content = build_article.build(article, plan)
        problems = build_article.check(content, article, plan)
        with open(os.path.join(workspace, "content.html"), "w") as fh:
            fh.write(content)
        with open(os.path.join(workspace, "preview.html"), "w") as fh:
            fh.write(build_article.preview(content, article, plan, problems))
        print("Dry run. Nothing was uploaded or created.")
        print(f"  images that would upload: {len(images)}")
        for i in images:
            mark = "ok " if i.get("_path") and os.path.exists(i["_path"]) else "MISSING"
            print(f"    [{mark}] {i.get('_path')}")
        print(f"  status would be: {plan.get('status', 'draft')}")
        if problems:
            print("\nBefore publishing:")
            for p in problems:
                print(f"  - {p}")
        return 0

    base = os.environ.get("WP_URL")
    user = os.environ.get("WP_USER")
    app_pw = os.environ.get("WP_APP_PASSWORD")
    if not all([base, user, app_pw]):
        raise SystemExit("Set WP_URL, WP_USER and WP_APP_PASSWORD. See the skill's README.")

    wp = WordPress(base, user, app_pw)
    me = wp.whoami()
    print(f"Authenticated as {me.get('name')} ({', '.join(me.get('roles', []))})")

    for img in images:
        media = wp.upload_media(img["_path"], alt=img.get("alt"),
                                title=img.get("caption") or None)
        img["id"] = media["id"]
        img["url"] = media["source_url"]
        print(f"  uploaded {os.path.basename(img['_path'])} -> {media['id']}")

    plan["images"] = images
    content = build_article.build(article, plan)
    problems = build_article.check(content, article, plan)

    dek = plan.get("dek") or article.get("dek") or ""
    seo = plan.get("seo", {})
    payload = {
        "title": plan.get("title") or article.get("hed") or "",
        "status": plan.get("status", "draft"),
        "content": content,
        "excerpt": dek,
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
    unresolved_bylines = []
    if plan.get("coauthors"):
        ids, unresolved_bylines = wp.resolve_coauthors(plan["coauthors"])
        if ids:
            payload["coauthors"] = ids

    lead = next((i for i in images if i.get("lead")), images[0] if images else None)
    if lead and lead.get("id"):
        payload["featured_media"] = lead["id"]

    post = wp.create_post(payload)
    print(f"\nCreated {post['status']} post {post['id']}: {post['title']['rendered']}")
    print(f"  edit:    {base.rstrip('/')}/wp-admin/post.php?post={post['id']}&action=edit")
    print(f"  preview: {post.get('link')}")

    with open(os.path.join(workspace, "content.html"), "w") as fh:
        fh.write(content)
    with open(os.path.join(workspace, "published.json"), "w") as fh:
        json.dump({"id": post["id"], "link": post.get("link"),
                   "status": post["status"], "images": images}, fh, indent=2)

    if unresolved_bylines:
        problems.append(
            "Byline not set for " + ", ".join(unresolved_bylines)
            + ". Set it in the Authors box in WP admin.")

    if problems:
        print("\nBefore publishing:")
        for p in problems:
            print(f"  - {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
