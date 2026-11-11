import os
import re
import json
import html
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.parse import quote

OWNER = "tahliaparker"
REPO = "window-consultant"
BASE_PATH = "/window-consultant/"
SITE_TITLE = "Window Consultant"
SITE_DESCRIPTION = (
    "Practical insights on window repair, maintenance, "
    "glass care, and home improvement."
)

SITE_URL = f"https://{OWNER}.github.io{BASE_PATH}"
OUTPUT = Path("site")
POSTS = OUTPUT / "posts"
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN", "")


def github_api(url):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "WindowConsultantPublisher",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"

    request = Request(url, headers=headers)
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def get_issues():
    issues = []
    page = 1

    while True:
        url = (
            f"https://api.github.com/repos/{OWNER}/{REPO}/issues"
            f"?state=open&per_page=100&page={page}"
        )
        batch = github_api(url)
        issues.extend(
            item for item in batch if "pull_request" not in item
        )
        if len(batch) < 100:
            break
        page += 1

    return sorted(
        issues,
        key=lambda item: item["created_at"],
        reverse=True,
    )


def slugify(value):
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")[:70] or "article"


def render_text(value):
    value = html.escape(value or "")
    value = re.sub(
        r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
        lambda m: (
            f'<a href="{html.escape(m.group(2), quote=True)}" '
            f'rel="noopener noreferrer">{m.group(1)}</a>'
        ),
        value,
    )
    paragraphs = re.split(r"\n\s*\n", value)
    return "\n".join(
        f"<p>{p.replace(chr(10), '<br>')}</p>"
        for p in paragraphs if p.strip()
    )


def page_template(title, body, description=""):
    safe_title = html.escape(title)
    safe_description = html.escape(description, quote=True)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{safe_title} | {SITE_TITLE}</title>
<meta name="description" content="{safe_description}">
<style>
* {{ box-sizing: border-box; }}
body {{
    margin: 0;
    font-family: Arial, Helvetica, sans-serif;
    background: #f7f9f8;
    color: #26352f;
    line-height: 1.75;
}}
header {{
    background: #23483c;
    padding: 25px 20px;
    text-align: center;
}}
header a {{
    color: white;
    text-decoration: none;
    font-size: 27px;
    font-weight: bold;
}}
main {{
    max-width: 850px;
    margin: 40px auto;
    padding: 35px;
    background: white;
    border-radius: 12px;
}}
h1 {{ line-height: 1.3; }}
a {{ color: #24725b; }}
article {{
    border-bottom: 1px solid #e5eae7;
    padding-bottom: 22px;
    margin-bottom: 22px;
}}
time {{ color: #65756d; font-size: 14px; }}
footer {{
    text-align: center;
    padding: 30px;
    color: #65756d;
    font-size: 14px;
}}
@media(max-width: 600px) {{
    main {{ margin: 15px; padding: 20px; }}
}}
</style>
</head>
<body>
<header><a href="{BASE_PATH}">{SITE_TITLE}</a></header>
<main>{body}</main>
<footer>© {datetime.now(timezone.utc).year} {SITE_TITLE}.
All rights reserved.</footer>
</body>
</html>"""


def main():
    POSTS.mkdir(parents=True, exist_ok=True)
    issues = get_issues()
    cards = []
    sitemap_urls = [SITE_URL]
    active_files = set()

    for issue in issues:
        title = issue.get("title", "Untitled")
        content = issue.get("body") or ""
        date = issue["created_at"][:10]
        filename = f'{issue["number"]}-{slugify(title)}.html'
        active_files.add(filename)

        relative_url = f"posts/{quote(filename)}"
        article_url = SITE_URL + relative_url

        article_body = f"""
<article>
<h1>{html.escape(title)}</h1>
<time datetime="{date}">{date}</time>
<div>{render_text(content)}</div>
<p><a href="{BASE_PATH}">← Back to articles</a></p>
</article>
"""
        (POSTS / filename).write_text(
            page_template(title, article_body, content[:155]),
            encoding="utf-8",
        )

        cards.append(f"""
<article>
<h2><a href="{relative_url}">{html.escape(title)}</a></h2>
<time datetime="{date}">{date}</time>
<p>{html.escape(re.sub(r'\\s+', ' ', content)[:180])}...</p>
<a href="{relative_url}">Read article →</a>
</article>
""")
        sitemap_urls.append(article_url)

    for old_file in POSTS.glob("*.html"):
        if old_file.name not in active_files:
            old_file.unlink()

    homepage = (
        f"<h1>Latest Articles</h1>"
        f"<p>{SITE_DESCRIPTION}</p>"
        + (
            "\n".join(cards)
            if cards
            else "<p>New articles are coming soon.</p>"
        )
    )

    (OUTPUT / "index.html").write_text(
        page_template(SITE_TITLE, homepage, SITE_DESCRIPTION),
        encoding="utf-8",
    )

    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(
            f"<url><loc>{html.escape(url)}</loc></url>\n"
            for url in sitemap_urls
        )
        + "</urlset>"
    )

    (OUTPUT / "sitemap.xml").write_text(
        sitemap, encoding="utf-8"
    )

    (OUTPUT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}sitemap.xml\n",
        encoding="utf-8",
    )

    (OUTPUT / ".nojekyll").touch()

    print(f"Published {len(issues)} articles for {SITE_TITLE}")


if __name__ == "__main__":
    main()
