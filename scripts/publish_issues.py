import os
import re
import json
import html
from pathlib import Path
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.parse import quote

OWNER = "tahliaparker"
REPO = "window-consultant"
BASE_PATH = "/window-consultant/"
SITE_TITLE = "Window Consultant"
SITE_DESCRIPTION = (
    "Thoughtful advice on window care, glass repair, "
    "maintenance, and comfortable living spaces."
)
SITE_URL = f"https://{OWNER}.github.io{BASE_PATH}"

OUTPUT = Path("site")
POSTS = OUTPUT / "posts"
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get(
    "GITHUB_TOKEN", ""
)


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

    def markdown_link(match):
        url = html.escape(match.group(2), quote=True)
        label = match.group(1)
        return (
            f'<a href="{url}" rel="noopener noreferrer">'
            f"{label}</a>"
        )

    value = re.sub(
        r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
        markdown_link,
        value,
    )

    paragraphs = re.split(r"\n\s*\n", value)
    return "\n".join(
        "<p>" + p.replace("\n", "<br>") + "</p>"
        for p in paragraphs if p.strip()
    )


CSS = """
:root {
    --olive: #535d3c;
    --olive-dark: #343d29;
    --sand: #e9dfca;
    --cream: #faf8f2;
    --paper: #fffefb;
    --ink: #30352d;
    --muted: #777b6c;
    --line: #e5dfd1;
}
* {
    box-sizing: border-box;
}
body {
    margin: 0;
    background: var(--cream);
    color: var(--ink);
    font-family: Georgia, "Times New Roman", serif;
    line-height: 1.75;
}
a {
    color: var(--olive);
}
.site-header {
    background: var(--sand);
    border-bottom: 1px solid #d8ccb4;
}
.header-inner {
    max-width: 1120px;
    margin: auto;
    padding: 30px 28px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 24px;
}
.brand {
    color: var(--olive-dark);
    font-size: 29px;
    font-weight: bold;
    letter-spacing: -0.7px;
    text-decoration: none;
}
.header-note {
    font-family: Arial, sans-serif;
    color: var(--olive);
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 2px;
}
.hero {
    max-width: 1120px;
    margin: auto;
    padding: 75px 28px 45px;
}
.eyebrow {
    color: var(--olive);
    font-family: Arial, sans-serif;
    font-size: 12px;
    font-weight: bold;
    letter-spacing: 2.5px;
    text-transform: uppercase;
}
.hero h1 {
    max-width: 760px;
    margin: 14px 0;
    font-size: clamp(42px, 6vw, 72px);
    line-height: 1.12;
    letter-spacing: -2px;
    font-weight: normal;
}
.hero p {
    max-width: 640px;
    font-size: 19px;
    color: #686e5c;
}
.main-content {
    max-width: 1120px;
    margin: 0 auto 80px;
    padding: 0 28px;
}
.section-heading {
    border-top: 1px solid var(--line);
    padding-top: 25px;
    margin-bottom: 30px;
    font-family: Arial, sans-serif;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--olive);
}
.post-card {
    display: grid;
    grid-template-columns: 155px 1fr;
    gap: 32px;
    background: var(--paper);
    border: 1px solid var(--line);
    border-radius: 3px;
    padding: 35px;
    margin-bottom: 18px;
}
.post-date {
    color: var(--muted);
    font-family: Arial, sans-serif;
    font-size: 13px;
    letter-spacing: 1px;
}
.post-card h2 {
    font-size: 30px;
    line-height: 1.25;
    font-weight: normal;
    margin: 0 0 14px;
}
.post-card h2 a {
    color: var(--olive-dark);
    text-decoration: none;
}
.post-card h2 a:hover {
    text-decoration: underline;
}
.post-card p {
    color: #666b5e;
    margin: 0 0 18px;
}
.read-more {
    font-family: Arial, sans-serif;
    font-size: 12px;
    font-weight: bold;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    text-decoration: none;
}
.empty-state {
    padding: 50px;
    background: var(--paper);
    border: 1px solid var(--line);
    color: var(--muted);
    text-align: center;
}
.article-container {
    max-width: 850px;
    margin: 55px auto 90px;
    padding: 60px;
    background: var(--paper);
    border: 1px solid var(--line);
}
.article-container h1 {
    font-size: clamp(35px, 5vw, 52px);
    font-weight: normal;
    line-height: 1.2;
    margin: 15px 0 25px;
}
.article-content {
    font-size: 18px;
    overflow-wrap: anywhere;
}
.article-content p {
    margin-bottom: 22px;
}
.article-content a {
    text-decoration: underline;
}
.back-link {
    display: inline-block;
    margin-top: 35px;
    font-family: Arial, sans-serif;
    font-size: 13px;
    text-decoration: none;
}
.site-footer {
    background: var(--olive-dark);
    color: #e9e4d8;
    padding: 42px 28px;
}
.footer-inner {
    max-width: 1120px;
    margin: auto;
    display: flex;
    justify-content: space-between;
    gap: 20px;
    font-family: Arial, sans-serif;
    font-size: 13px;
}
@media (max-width: 700px) {
    .header-inner {
        padding: 23px 20px;
    }
    .brand {
        font-size: 23px;
    }
    .header-note {
        display: none;
    }
    .hero {
        padding: 50px 20px 35px;
    }
    .hero h1 {
        letter-spacing: -1px;
    }
    .main-content {
        padding: 0 20px;
    }
    .post-card {
        display: block;
        padding: 25px;
    }
    .post-date {
        display: block;
        margin-bottom: 15px;
    }
    .post-card h2 {
        font-size: 26px;
    }
    .article-container {
        margin: 20px;
        padding: 25px;
    }
    .footer-inner {
        flex-direction: column;
    }
}
"""


def page_template(title, body, description="", home=False):
    safe_title = html.escape(title)
    safe_description = html.escape(description, quote=True)
    full_title = (
        SITE_TITLE if home else f"{title} | {SITE_TITLE}"
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{safe_description}">
<style>{CSS}</style>
</head>
<body>
<header class="site-header">
    <div class="header-inner">
        <a class="brand" href="{BASE_PATH}">{SITE_TITLE}</a>
        <span class="header-note">Ideas for better living</span>
    </div>
</header>
{body}
<footer class="site-footer">
    <div class="footer-inner">
        <span>© {datetime.now(timezone.utc).year}
        {SITE_TITLE}. All rights reserved.</span>
        <span>Window Care · Glass · Home Improvement</span>
    </div>
</footer>
</body>
</html>"""


def main():
    POSTS.mkdir(parents=True, exist_ok=True)
    issues = get_issues()
    cards = []
    sitemap_urls = [SITE_URL]
    active_files = set()

    for issue in issues:
        title = issue.get("title") or "Untitled"
        content = issue.get("body") or ""
        date = issue["created_at"][:10]
        filename = f'{issue["number"]}-{slugify(title)}.html'
        active_files.add(filename)

        relative_url = f"posts/{quote(filename)}"
        article_url = SITE_URL + relative_url

        article_body = f"""
<main class="article-container">
    <span class="eyebrow">Window Consultant Journal</span>
    <h1>{html.escape(title)}</h1>
    <time class="post-date" datetime="{date}">{date}</time>
    <div class="article-content">
        {render_text(content)}
    </div>
    <a class="back-link" href="{BASE_PATH}">
        ← Back to all articles
    </a>
</main>
"""

        (POSTS / filename).write_text(
            page_template(title, article_body, content[:155]),
            encoding="utf-8",
        )

        summary = re.sub(r"\s+", " ", content).strip()
        excerpt = html.escape(summary[:180])
        if len(summary) > 180:
            excerpt += "..."

        cards.append(f"""
<article class="post-card">
    <time class="post-date" datetime="{date}">{date}</time>
    <div>
        <h2><a href="{relative_url}">
            {html.escape(title)}
        </a></h2>
        <p>{excerpt}</p>
        <a class="read-more" href="{relative_url}">
            Read Article →
        </a>
    </div>
</article>
""")
        sitemap_urls.append(article_url)

    for old_file in POSTS.glob("*.html"):
        if old_file.name not in active_files:
            old_file.unlink()

    cards_html = (
        "\n".join(cards)
        if cards
        else (
            '<div class="empty-state">'
            "New articles are coming soon."
            "</div>"
        )
    )

    homepage = f"""
<section class="hero">
    <span class="eyebrow">The Window Consultant Edit</span>
    <h1>Better windows.<br>Better living.</h1>
    <p>{SITE_DESCRIPTION}</p>
</section>
<main class="main-content">
    <h2 class="section-heading">Latest Stories</h2>
    {cards_html}
</main>
"""

    (OUTPUT / "index.html").write_text(
        page_template(
            SITE_TITLE, homepage, SITE_DESCRIPTION, home=True
        ),
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

    print(
        f"Published {len(issues)} articles for {SITE_TITLE}"
    )


if __name__ == "__main__":
    main()
