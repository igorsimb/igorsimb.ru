# Redesign Implementation Handoff

**Status:** Design approved. The next task is Django implementation.

## Read in This Order

1. [`redesign-brief.md`](redesign-brief.md) defines positioning, content hierarchy, language behavior, and product boundaries.
2. [`prototypes/README.md`](prototypes/README.md) defines the visual system, responsive behavior, and exact alignment rules.
3. [`implementation-notes.md`](implementation-notes.md) defines Django data changes, template constraints, tests, and work order.
4. Compare implementation directly with the three final references:
   - [`prototypes/homepage.html`](prototypes/homepage.html)
   - [`prototypes/blog-index.html`](prototypes/blog-index.html)
   - [`prototypes/blog-article.html`](prototypes/blog-article.html)

## Source-of-Truth Rules

- Use the brief for content, positioning, and feature behavior.
- Use the visual guide and HTML references for layout, spacing, color, typography, and responsive intent.
- Use the implementation notes for Django models, queries, templates, and tests.
- If a prototype contains `#` links or a prototype-identification strip, treat them as documentation placeholders, not
  production requirements.
- Do not introduce another design direction, frontend framework, CMS, component library, or dependency upgrade.

## Definition of Done for the First Implementation

- Homepage, blog index, and article detail match the approved references at phone, laptop, and wide desktop sizes.
- Shared navigation is sticky, keyboard accessible, and usable on mobile.
- EN/RU interface behavior is preserved; English-only articles remain honestly English-only.
- Featured articles are managed through Django admin and obey the ordering and fallback rules.
- Article content renders safely with readable headings, lists, code, links, images, and bounded wide elements.
- Resume and case-study actions never point to missing resources.
- Focused pytest coverage and Django system checks pass.
- No page has horizontal overflow, duplicate footers, or prototype-only labels.

Dedicated case-study pages are a later content-and-design task. Do not invent them during the first implementation.
