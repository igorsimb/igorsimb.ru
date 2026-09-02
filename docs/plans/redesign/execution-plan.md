# Portfolio Redesign Execution Plan

**Status:** Approved for implementation

**Purpose:** This is the operational checklist for an LLM implementing the redesign. Follow it in order, update the
checkboxes as work is completed, and do not rely on conversation history for requirements.

## 1. Mandatory Context

Before editing code, read these files completely in this order:

1. [`redesign-brief.md`](redesign-brief.md)
2. [`prototypes/README.md`](prototypes/README.md)
3. [`implementation-notes.md`](implementation-notes.md)
4. [`prototypes/homepage.html`](prototypes/homepage.html)
5. [`prototypes/blog-index.html`](prototypes/blog-index.html)
6. [`prototypes/blog-article.html`](prototypes/blog-article.html)
7. This execution plan

Also inspect `AGENTS.md`, the current worktree status, and every file before modifying it. Preserve unrelated user
changes.

## 2. Final Decisions and Conflict Resolution

These decisions supersede any conflicting or less-specific wording elsewhere in the redesign documents:

- The three HTML prototypes are the final approved visual design. Do not add a separate Engineering Focus section. The
  operating-scale panel's Engineering Focus entry is sufficient.
- Remove the public contact form. The redesigned contact section has one direct email action using the existing address.
  Do not retain form fields or mail-delivery behavior on the homepage.
- `Post.summary` is optional plain-text editorial copy. It is not necessarily a TL;DR and must not be labeled as one by
  default.
- When `Post.summary` is blank, generate display copy from the beginning of `rendered_html`: strip HTML, normalize
  whitespace, and truncate to approximately 32 words. Never excerpt raw Markdown.
- An explicit `Post.summary` always wins over the generated fallback.
- Homepage featured article choices are controlled through Django admin. Show up to three published posts explicitly
  marked featured in the large-card section. Do not fill empty featured positions with recent posts.
- The homepage Latest Articles section shows up to three newest published posts not marked featured. A featured post
  never appears in Latest Articles.
- The homepage must never hard-code the placeholder article titles or descriptions from the prototype.
- The prototype's large case-card design is used for real featured articles; the placeholder case studies are omitted.
- Display headlines do not end with periods. This applies in both English and Russian, but not to paragraph copy or
  author-entered article titles.
- The shared navigation labels the homepage featured-article anchor `Featured` in English and `Избранное` in Russian.
- Blog articles remain English-only until real translations exist. EN/RU translates shared interface text without
  implying that an article has a Russian version.
- The authenticated blog dashboard and editor have no separate approved prototype. Redesign them after the public
  article detail using the same editorial-industrial visual language while preserving all existing author workflows.

When another document conflicts with this section, follow this section. Do not silently invent a third interpretation.

## 3. Scope Guardrails

### In scope

- Shared public header, accessible mobile navigation, language control, and footer.
- Homepage matching the approved homepage prototype.
- Database-backed homepage article selection.
- Blog index matching the approved ledger prototype.
- Blog detail layout and safe Markdown presentation matching the approved article prototype.
- `Post` featured, priority, summary, and tag data.
- Django admin controls for the new article data.
- Authenticated blog dashboard and writing-workspace redesign without changing their behavior or permissions.
- Focused pytest coverage, Django checks, and responsive/accessibility smoke checks.
- Removal of the public homepage contact form and now-unused contact-view behavior.

### Out of scope

- Dedicated case-study pages or invented private-case details.
- A CMS, frontend framework, Django Cotton, search, filtering, or table of contents.
- Article translation records or fake translated article URLs.
- Redesigning Django admin, store, accounts, or legacy project pages.
- Dependency upgrades, Tailwind build tooling, or removal of unrelated legacy assets.
- Commits, pushes, or pull requests unless explicitly requested.

## 4. Required Data Behavior

Extend `blog.models.Post` with:

- `is_featured`: boolean, default `False`.
- `feature_priority`: small integer with a sensible default. Lower numbers rank first.
- `summary`: optional blank plain-text field suitable for several sentences.
- `tags`: optional blank comma-separated display field.

Implement reusable model/query presentation behavior rather than duplicating selection rules across views.

### Published-post rules

- A public post has `status=published`.
- Drafts are excluded everywhere public, even if `is_featured=True`.
- Featured ordering is `feature_priority`, then newest `published_at`, then primary key for deterministic ties.
- Non-featured ordering is newest `published_at`, then primary key.
- Homepage selection algorithm:
  1. Select up to three featured published posts in featured order.
  2. Select up to three newest published posts with `is_featured=False` for the Latest Articles section.
  3. Keep the two sections mutually exclusive and never fill empty featured positions automatically.
- Blog index algorithm:
  1. Show every featured published post first in featured order and mark it Featured.
  2. Show every remaining published post afterward in reverse publication order.
  3. Never show a featured post twice.

### Presentation helpers

- Provide one summary-display helper that returns explicit, trimmed `summary` or a roughly 32-word plain-text fallback
  derived from `rendered_html`.
- Provide one tag-display helper that splits the comma-separated field, trims whitespace, and omits empty values.
- Keep helpers deterministic and usable from both homepage and blog templates.
- Do not add related-project model fields during this pass. Omit related-project metadata when no source data exists.

## 5. Implementation Phases

Complete and validate each phase before moving to the next. If interrupted, resume from the first unchecked validation
item rather than repeating completed work.

### Phase 0: Baseline and inventory

- [x] Confirm the worktree state with `git status --short` and record unrelated changes mentally before editing.
- [x] Inspect current model, migration, admin, views, URLs, templates, static files, locale catalog, sitemap, and tests.
- [x] Confirm the existing English and Russian resume files and the existing email destination.
- [x] Add root `pytest.ini` with `DJANGO_SETTINGS_MODULE = igorsimb.settings` and test discovery for app-level
      `tests.py`.
- [x] Run the existing focused tests and `manage.py check`; record any pre-existing failures before changing behavior.

Validation gate:

- [x] Pytest discovers the current Django tests.
- [x] Baseline failures, if any, are distinguishable from redesign regressions.

### Phase 1: Post data, migration, admin, and queries

Likely files:

- `blog/models.py`
- `blog/admin.py` (create if absent)
- `blog/migrations/0002_*.py`
- `blog/views.py`
- `blog/tests.py`

Tasks:

- [x] Add the four approved `Post` fields with a reviewable migration.
- [x] Add summary and tag presentation helpers.
- [x] Add reusable featured-homepage and ordered-index query behavior.
- [x] Register `Post` in Django admin.
- [x] Show title, status, featured state, priority, and publication date in the admin list.
- [x] Make featured state and priority editable from the admin list.
- [x] Make summary and tags easy to edit on the admin change form.
- [x] Preserve the custom Markdown editor's current field scope so it cannot erase admin-managed fields.
- [x] Update homepage context to expose up to three explicitly featured posts plus three latest non-featured posts.
- [x] Update blog index context to expose the single ordered ledger.
- [x] Add deterministic adjacent-article context for detail navigation if the template uses it.
- [x] Preserve graceful handling when the blog table is unavailable.

Validation gate:

- [x] Featured priority ordering passes.
- [x] Equal-priority date and primary-key ties pass deterministically.
- [x] Draft exclusion passes, including a draft marked featured.
- [x] Latest-post selection excludes all posts marked featured, without duplicates.
- [x] Explicit summary wins and blank summary produces a safe plain-text excerpt.
- [x] Tags trim cleanly and blank tags render no tag container.
- [x] Migration applies cleanly to an existing database.

### Phase 2: Shared public shell

Likely files:

- `core/templates/core/base.html`
- `core/templates/core/partials/header.html`
- `core/templates/core/partials/footer.html`
- `core/templatetags/navigation.py`
- `core/static/core/css/` and `core/static/core/js/` only where useful
- `locale/ru/LC_MESSAGES/django.po`

Tasks:

- [x] Introduce the approved Tailwind CDN configuration and public redesign tokens.
- [x] Remove the prototype-identification strip.
- [x] Implement one sticky public header shared by homepage, blog index, and article detail.
- [x] Use `IGOR SIMBIRTSEV /` on the homepage and `IGOR SIMBIRTSEV / BLOG` on blog pages.
- [x] Implement conventional desktop navigation and an accessible mobile disclosure control.
- [x] Ensure mobile navigation has an accessible name, correct expanded state, keyboard operation, and a no-JavaScript
      fallback for essential links.
- [x] Preserve locale selection and current-page behavior.
- [x] Ensure the blog locale switch keeps the English article URL and changes shared interface language only.
- [x] Select the English or Russian resume asset by interface locale and hide the action if the chosen file is
      unavailable.
- [x] Implement one shared footer with current year, GitHub, LinkedIn, and email links.
- [x] Prevent legacy base CSS/JS from distorting the public redesign while preserving editor/dashboard behavior.
- [x] Add visible focus styles and respect `prefers-reduced-motion`.

Validation gate:

- [x] Header and footer render exactly once on every public target page.
- [x] Mobile navigation works by keyboard and pointer.
- [x] Essential navigation remains usable without JavaScript.
- [x] EN/RU switches preserve core routes and do not manufacture article translations.
- [x] Missing resume produces no broken action.

### Phase 3: Homepage

Likely files:

- `core/views.py`
- `core/templates/core/index.html`
- focused partials for genuinely repeated case/article cards
- `core/tests.py`
- Russian locale catalog

Tasks:

- [x] Rebuild the homepage in the exact section order shown by `prototypes/homepage.html`.
- [x] Match the hero grid, approved copy, actions, operating-scale panel, colors, rules, typography, and responsive
      collapse.
- [x] Keep the approved public metrics exactly qualified: `10M+`, `~3.6 TB`, and `~15`.
- [x] Render up to three admin-selected articles using the approved large-card design and one consistent surface.
- [x] Link each featured article card to its real blog detail route.
- [x] Implement the dark coding-agent workflow with the five approved scan labels and copy.
- [x] Do not add a standalone Engineering Focus section.
- [x] Render up to three latest published non-featured articles beneath the featured section.
- [x] Use summary-display and tag-display behavior in both article sections; do not hard-code prototype articles.
- [x] Implement the approved About section.
- [x] Implement the orange contact band with a direct `mailto:` action only.
- [x] Remove homepage contact-form handling, fields, and now-unused imports while leaving unrelated email configuration
      alone.
- [x] Ensure resume actions are locale-correct and hidden if unavailable.

Validation gate:

- [x] Homepage works with zero, one, two, and three or more featured and latest posts.
- [x] Homepage featured selection follows Phase 1 rules.
- [x] Latest articles are chronological and exclude every post marked featured.
- [x] No placeholder article title is present unless it exists in the database.
- [x] No contact form remains in the public homepage HTML.
- [x] Every featured card links to an existing article route; no card contains `href="#"`.
- [x] Hero content and both actions fit at 1440x800.

### Phase 4: Blog index ledger

Likely files:

- `blog/templates/blog/index.html`
- reusable article-card partial
- shared public-site styles
- `blog/tests.py`

Tasks:

- [x] Match `prototypes/blog-index.html` while replacing all placeholder content with `Post` data.
- [x] Render one ledger only.
- [x] Mark featured entries visibly and place them first.
- [x] Render publication date, title, summary-display copy, optional tags, and a clear detail link for each post.
- [x] Keep superuser writing/dashboard actions available without disrupting the approved public hierarchy, or place them
      in a restrained authenticated-only utility location.
- [x] Provide a deliberate translated empty state without adding a promotional section.
- [x] Preserve canonical URL and sitemap behavior.

Validation gate:

- [x] Empty and partially populated indexes render without malformed borders or spacing.
- [x] Featured posts are pinned, marked once, and never duplicated.
- [x] Drafts never render.
- [x] No-tags rows omit the tag group cleanly.

### Phase 5: Blog article detail

Likely files:

- `blog/templates/blog/detail.html`
- `blog/static/blog/css/blog.css` or shared public styles
- `blog/rendering.py` only if safe rendering support requires a focused correction
- `blog/tests.py`

Tasks:

- [x] Match the approved article header, left-anchored 880px reading column, asymmetrical whitespace, navigation, and
      footer.
- [x] Show publication date and optional tags once in the header.
- [x] Use explicit `Post.summary` as optional short header copy when present. Do not invent or label a fallback as
      TL;DR.
- [x] Do not add a TL;DR block when the author has not explicitly supplied summary copy.
- [x] Do not add related-project UI without real source data.
- [x] Render stored sanitized `rendered_html` safely.
- [x] Style headings, paragraphs, ordered and unordered lists, inline code, fenced code, links, images, figures,
      tables, and captions consistently with the approved design.
- [x] Bound code, tables, and wide media inside internal horizontal-overflow containers.
- [x] Prevent page-level horizontal scrolling.
- [x] Keep article metadata in one place and do not add a body rail or table of contents.
- [x] Align top back link and ending navigation to the 880px reading axis.
- [x] Render a deterministic adjacent-article link when one exists and omit it cleanly otherwise.

Validation gate:

- [x] Headings, lists, code, links, and images survive rendering and remain contained.
- [x] Sanitization tests continue to reject unsafe HTML.
- [x] Blank summary does not create a TL;DR label or empty highlighted block.
- [x] Detail pages remain English articles under both interface locales and expose honest language metadata.
- [x] Detail page has one article footer/navigation region and one site footer.

### Phase 6: Author dashboard and writing workspace

Likely files:

- `blog/templates/blog/dashboard.html`
- `blog/templates/blog/editor.html`
- `blog/static/blog/css/blog.css`
- existing editor JavaScript only where presentation integration requires it
- `blog/tests.py`

Tasks:

- [x] Redesign `/blog/dashboard/`, `/blog/write/`, and `/blog/write/<pk>/` in the same editorial-industrial visual
      language as the approved public redesign.
- [x] Preserve the existing superuser-only authorization boundary and anonymous/non-superuser behavior.
- [x] Keep draft and published-post groupings, status metadata, edit actions, and new-post action clear on the
      dashboard.
- [x] Preserve every existing editor workflow: create, edit, save, autosave, publish, unpublish, preview modes, image
      upload, drag-and-drop, validation messages, and public-article link.
- [x] Keep the writing surface and rendered preview legible at desktop widths and usable on phone and tablet widths.
- [x] Use restrained author-only navigation back to the public blog and between dashboard and editor.
- [x] Do not change post data semantics, public permissions, or editor API contracts as part of the visual redesign.

Validation gate:

- [x] Anonymous users still redirect to login and authenticated non-superusers remain forbidden.
- [x] Dashboard empty, draft-only, published-only, and mixed states render cleanly.
- [x] Creating, editing, saving, publishing, unpublishing, previewing, and uploading valid images still pass.
- [x] Invalid form and upload states remain visible, understandable, and non-destructive.
- [x] Dashboard and editor have no page-level overflow at the required visual QA widths.

### Phase 7: Translation, accessibility, metadata, and cleanup

Tasks:

- [x] Add English source strings and complete Russian translations for all shared public interface copy.
- [x] Compile translations using the existing project workflow and verify visible Russian output.
- [x] Set `<html lang>` from the active interface language.
- [x] Verify semantic landmarks, one logical `h1`, heading order, link names, alt text, focus visibility, and contrast.
- [x] Verify canonical URLs, descriptions, sitemap entries, and robots behavior.
- [x] Remove imports, code, templates, and tests made unused specifically by removing the contact form.
- [x] Do not remove unrelated legacy assets or code.
- [x] Review the final diff for prototype-only labels, dead links, duplicate content, and accidental formatting churn.

Validation gate:

- [x] English and Russian public routes render successfully.
- [x] Missing translations visibly fall back to English rather than blank text.
- [x] Article language behavior is honest and canonical URLs remain stable.
- [x] No prototype-identification strip or `#` placeholder action remains.

### Phase 8: Final verification

Run the narrowest relevant checks after each phase, then finish with:

```powershell
.venv\Scripts\python.exe -m pytest
.venv\Scripts\python.exe manage.py check
.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
```

Also perform production-like page smoke checks with `DEBUG=False` where the existing settings make that safe.

Visual QA widths:

- [ ] Phone: approximately 375px.
- [ ] Tablet: approximately 768px.
- [ ] Laptop: 1440x800, including full hero content and actions.
- [ ] Wide desktop: approximately 1920px.

At every width verify:

- [ ] No page-level horizontal overflow.
- [ ] Header, navigation, language control, and resume action remain usable.
- [ ] Long titles, tags, code, images, and case metadata stay contained.
- [ ] Reading-column and grid alignment match the prototypes.
- [ ] Hover motion is nonessential and reduced-motion preferences are respected.

## 6. Required Test Matrix

Do not mark the implementation complete without automated coverage for these observable behaviors:

- [ ] Featured ordering by priority.
- [ ] Deterministic equal-priority ordering.
- [ ] Draft exclusion even when featured.
- [ ] Homepage featured and latest sections remain mutually exclusive and each respects its three-post cap.
- [ ] Explicit summary and generated plain-text fallback.
- [ ] Tags and no-tags presentation.
- [ ] Empty and populated blog index.
- [ ] Featured index pinning without duplication.
- [ ] Article Markdown headings, lists, code, links, and images.
- [ ] Sanitized unsafe Markdown/HTML.
- [ ] English and Russian shared interfaces.
- [ ] English-only article behavior under a Russian interface.
- [ ] Locale-aware and missing-resume behavior.
- [ ] Email-only contact section.
- [ ] Hidden unavailable case-study actions.
- [ ] Existing editor saves do not overwrite admin-managed fields.

Prefer behavior assertions over exact utility-class or prose assertions unless exact text is an approved public
requirement.

## 7. LLM Working Protocol

- Work phase by phase. Do not start a later phase while the current phase has unexplained failing checks.
- Before each edit, reopen the touched file and inspect nearby conventions. Never reconstruct it from memory.
- Use small patches. Avoid broad template rewrites that accidentally remove metadata, locale, analytics, or authoring
  hooks.
- After each patch, inspect `git diff --check` and the focused diff.
- Never overwrite unrelated worktree changes. If user edits overlap the current file, reconcile deliberately.
- Do not claim visual fidelity from template inspection alone. Render and inspect all three public surfaces at the
  required widths before completion.
- If context is compacted, reread Section 2 and resume at the first unchecked item in Section 5.
- If a new ambiguity affects visible behavior, stop and ask. For minor internal choices, prefer the simplest solution
  that follows existing Django conventions and this plan.
- Do not commit, push, deploy, or write to external services without explicit user authorization.

## 8. Completion Report

The final handoff must state:

- The user-visible outcome.
- The principal files and migration changed.
- The exact test and check commands that passed.
- The widths and pages visually inspected.
- Any material validation gap or deferred item.
- A suggested Conventional Commit message covering the complete redesign, because repository files changed.

The task is complete only when all in-scope phases and required validation gates are satisfied. Passing tests alone is
not sufficient without responsive visual verification against all three prototypes.
