from html import escape

import bleach
import markdown

ALLOWED_TAGS = list(bleach.sanitizer.ALLOWED_TAGS) + [
    "p",
    "pre",
    "code",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
    "br",
    "div",
    "img",
    "span",
    "table",
    "thead",
    "tbody",
    "tr",
    "th",
    "td",
    "figure",
    "figcaption",
]
ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "rel"],
    "code": ["class"],
    "div": ["class"],
    "img": ["alt", "src", "title"],
    "span": ["class"],
}


def normalize_article_html(rendered_html: str) -> str:
    return rendered_html.replace("<h1>", "<h2>").replace("</h1>", "</h2>")


def render_markdown(markdown_body: str) -> str:
    escaped_markdown = escape(markdown_body or "", quote=False)
    html = markdown.markdown(
        escaped_markdown,
        extensions=["extra", "fenced_code", "codehilite", "sane_lists"],
        output_format="html5",
    )

    sanitized_html = bleach.clean(
        html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True
    )
    return normalize_article_html(sanitized_html)
