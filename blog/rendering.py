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
]
ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "rel"],
    "code": ["class"],
    "div": ["class"],
    "img": ["alt", "src", "title"],
    "span": ["class"],
}


def render_markdown(markdown_body: str) -> str:
    escaped_markdown = escape(markdown_body or "", quote=False)
    html = markdown.markdown(
        escaped_markdown,
        extensions=["extra", "fenced_code", "codehilite", "sane_lists"],
        output_format="html5",
    )

    return bleach.clean(
        html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True
    )
