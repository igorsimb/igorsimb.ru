# Django Implementation Notes

**Status:** Ready for implementation. No redesign code has been applied to the Django site.

## Initial Implementation Scope

Implement these surfaces from the final references:

1. Shared header, mobile navigation, language control, and footer.
2. Homepage layout and sections.
3. Blog index ledger.
4. Blog article layout and Markdown presentation styles.
5. Admin-managed featured-article fields and selection behavior.
6. Focused pytest coverage for the new data and rendering behavior.

Dedicated engineering case-study pages are not visually specified yet. Do not invent them during this pass. Homepage case
cards may be implemented, but unavailable actions must be hidden rather than linked to `#`.

## Three-Year Content Horizon

The portfolio structure should remain mostly stable for at least three years. New blog articles will be the main recurring
change. Keep the implementation simple:

- Render the site with Django templates.
- Keep articles in the existing database-backed Markdown workflow.
- Implement the initial case studies as stable pages unless a real editing need appears.
- Do not add a CMS, page builder, or frontend framework.
- Keep shared facts in one place so homepage summaries and case pages cannot contradict each other.
- Preserve stable URLs, semantic HTML, translated interface strings, and a small set of design tokens.

## Coding-Agent Section

Add a compact **How I work with coding agents** section after the featured case studies. It explains a part of Igor's daily
engineering work that a reviewer is likely to ask about.

The section describes how decisions are made, how generated code is reviewed, and how the result is verified. It does not
lead with the percentage of generated code. Dux provides the detailed public example.

## Admin-Managed Featured Articles

The homepage should not hard-code article choices. Extend the existing `Post` model with:

- `is_featured`, a boolean controlled in Django admin;
- `feature_priority`, a small integer used to order featured posts;
- `summary`, optional plain-text card copy;
- `tags`, an optional comma-separated display field.

Show up to three published posts. Explicitly featured posts come first, ordered by priority and then publication date. Fill
any remaining positions with the latest published posts. A draft never appears, even when marked as featured.

When `summary` is blank, build the card excerpt from `rendered_html`: strip HTML and truncate the plain text to about 32
words. Do not excerpt raw Markdown, because headings, links, and code syntax make poor card copy. Hide the tag row when no
tags are supplied. Equal priorities should resolve by publication date and then primary key so ordering is deterministic.

Register `Post` in Django admin with title, status, featured state, priority, and publication date visible in the list. Make
featured state and priority editable there. The existing custom Markdown editor may remain focused on writing; its
`ModelForm` only saves `title` and `markdown_body`, so it will not overwrite the new fields.

The blog index uses one article ledger rather than separate featured and archive grids. Featured posts are pinned to the top
and marked with a small label; all other posts follow in reverse publication order. This avoids showing the same article
twice and remains easy to scan as the archive grows. Dates, summaries, and optional tags are visible in every row.

Article pages use a reading column of roughly 880 pixels, with wider technical elements placed inside bounded horizontal
overflow containers when necessary. Publication details, topics, and a related project link appear once in the article
header. Do not add a second metadata rail beside the body. Anchor the reading column to the left edge of the shared 1440px
page grid rather than centering it independently. Align the header's back link and the article-navigation row to the same
880px reading axis: back links begin at its left edge and the next-article title ends at its right edge.

Do not add a table of contents until the Markdown renderer produces stable heading IDs. The current renderer preserves
headings but does not create anchors, and a decorative table of contents with unreliable links would be worse than none.
Keep the article ending compact: a link back to the index and an adjacent-article link, followed by the normal site footer.

## Template Approach

Use regular Django templates with a few native `{% include %}` partials. Django Cotton will not be added.

Use an include only when markup is genuinely repeated, such as the header, footer, case-study card, or article card. Keep
one-off sections in their page templates. Some Tailwind classes may be repeated across templates. That is acceptable for a
site whose structure will rarely change.

The existing templates extend `core/base.html`, with shared fragments under `core/templates/core/partials/`. Preserve that
server-rendered structure and the current locale middleware. Suggested additions are a case card and article card partial;
do not split every homepage section into its own file.

The dark prototype-identification strip at the top of each HTML reference is documentation only. Production pages begin
with the sticky site header.

## Pytest Migration

The following versions are installed in the project environment:

```powershell
uv pip install "pytest==9.1.1" "pytest-django==4.14.0"
```

The implementation phase still needs a root `pytest.ini` similar to:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = igorsimb.settings
python_files = tests.py test_*.py *_tests.py
```

The `python_files` line matters because this repository currently keeps tests in app-level `tests.py` files. Database tests
can continue using Django `TestCase` and move gradually to pytest functions and fixtures. New database-using pytest functions
should request `db` or use `@pytest.mark.django_db`.

At minimum, test:

- featured ordering, recent-post fallback, deterministic priority ties, and draft exclusion;
- explicit summaries and generated plain-text summary fallbacks;
- optional tags and the no-tags rendering path;
- empty and partially populated blog indexes;
- article detail rendering for headings, lists, code, links, and images;
- English and Russian shared-interface routes without implying unavailable article translations;
- missing resume and unavailable case-study action behavior.

Source: [pytest-django documentation](https://pytest-django.readthedocs.io/en/latest/).

## Tailwind CDN Constraint

The prototypes use the Tailwind CDN as requested. It is fine for visual exploration and the initial implementation.

For production, the CDN compiles styles in the browser and adds a third-party request. It also makes a strict Content
Security Policy harder. Before deployment, decide whether to accept that or compile a pinned Tailwind stylesheet as a static
asset. Compiling Tailwind would not require a Django upgrade.

## Stable Homepage Copy

Avoid facts that expire merely with time or a change of job. Do not place the current sole-developer arrangement or a fixed
number of development years in the hero or About section. That work context can appear where it explains a specific case.
Render the footer year with Django's `{% now "Y" %}` tag rather than updating template text annually.

## Recommended Work Order

1. Add `pytest.ini` and establish passing baseline tests.
2. Add the `Post` fields, migration, Django admin registration, query logic, and model/view tests.
3. Implement shared design tokens, header, mobile navigation, language control, and footer.
4. Implement the homepage against `prototypes/homepage.html`.
5. Implement the blog index and article templates against their references.
6. Add responsive, accessibility, locale, metadata, and production-like smoke checks.

Keep each step reviewable. Do not mix removal of unrelated legacy assets or project-page rewrites into this implementation.
