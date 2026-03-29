# Implementation plan: remove Wagtail first, then build a new Django blog

## Objective

Replace the current Wagtail/Puput-powered blog with a new plain Django `blog` app built from a clean slate.

This project-specific plan follows this required sequence:

1. inventory all current Wagtail and Puput coupling in this repository
2. remove Wagtail, Puput, and the current `blog/` app completely
3. verify zero traces remain in code, settings, URLs, templates, and runtime
4. only then recreate `blog/` as a new plain Django app and implement the replacement blog

This is a full reset. No Wagtail content, data model, routes, templates, or compatibility behavior will be preserved.

## Project Decisions

- Public blog URL becomes `/blog/`.
- Remove the current `blog/` app entirely, then recreate a new app with the same name: `blog`.
- Datastar is served locally from the project's static assets, not from a CDN.
- Authoring is single-user and superuser-only.
- The writing experience should stay simple and low-friction, not CMS-like.
- Do not use a code editor such as CodeMirror by default. Prefer a clean Markdown writing interface with strong rendered code-block presentation and syntax highlighting in preview/public output.
- Implementation must be phase-based, and work stops after each phase for user review and approval.

## Current Project Reality

The current Wagtail/Puput coupling already identified in this repository includes:

- `requirements.txt`
  contains `puput`, `wagtail`, `wagtail-markdown`, and multiple Wagtail-adjacent packages that may become removable after dependency review
- `igorsimb/settings.py`
  imports `PUPUT_APPS`, appends `PUPUT_APPS` into `INSTALLED_APPS`, configures `wagtail.contrib.redirects.middleware.RedirectMiddleware`, and defines `WAGTAIL_*` settings
- `igorsimb/urls.py`
  mounts `path("read/", include("puput.urls"))`
- `core/templates/core/partials/header.html`
  links the site navigation to `/read/blog/`
- `blog/templates/puput/**`
  contains Puput templates with Wagtail template tags and Puput static assets
- `blog/static/css/custom_blog.css`
- `blog/static/css/main_nav_blog.css`
- `blog/apps.py`, `blog/models.py`, `blog/views.py`, `blog/admin.py`, `blog/tests.py`
  currently minimal, but the whole `blog/` app should still be removed as part of the clean reset

## Delivery Constraints

- Do not preserve Wagtail content, Wagtail models, Puput templates, or `/read/blog/` routing.
- Do not keep Wagtail installed "just in case".
- Do not add backwards compatibility for old blog URLs or old Wagtail data.
- Do not use Django admin as the primary writing interface.
- Do not build a general CMS.
- Do not add categories, tags, comments, revisions, scheduling, RSS, search, or multi-author workflows.
- Do not add a block editor or rich text editor.
- Keep the new blog implementation minimal, readable, and easy to maintain.

## Authoring Goal

The main product goal is a low-friction writing workflow for a single developer-author:

- quick access to drafts
- clean Markdown writing surface
- live preview without changing pages or mental context
- strong code-block rendering for technical posts
- fast image insertion without leaving the editor
- clear draft/published state

## Verification Strategy

Use the existing virtual environment for all checks:

- `".igorsimb_ru/Scripts/python.exe" manage.py check`
- `".igorsimb_ru/Scripts/python.exe" manage.py test`
- targeted grep checks for `wagtail` and `puput` references in the repository

Before implementation begins, each phase should define its own concrete verification step. After implementing a phase, stop and wait for user review.

## Review Gates

Every phase below ends with a hard stop:

- implement only that phase
- run the listed verification for that phase
- update `docs/plans/progress.md`
- stop and wait for user review/approval before starting the next phase

## Phase 1: Inventory Current Wagtail/Puput Usage

### Goal

Produce the deletion map for the current Wagtail/Puput implementation so removal is complete and intentional.

### Files and areas to inspect

- `requirements.txt`
- `igorsimb/settings.py`
- `igorsimb/urls.py`
- `core/templates/core/partials/header.html`
- `blog/` in full, especially:
  `blog/templates/puput/**`
  `blog/static/css/**`
  `blog/apps.py`
  `blog/models.py`
  `blog/views.py`
  `blog/admin.py`
  `blog/tests.py`
  `blog/migrations/**`

### Tasks

- enumerate all Wagtail and Puput dependencies used by the project
- confirm whether any non-blog app depends on Wagtail assumptions
- identify all routes, navigation links, template tags, and settings tied to the current blog
- identify every path that must change from `/read/blog/` to `/blog/` or to a temporary no-blog state during the removal phase
- produce the exact file deletion and edit list for phase 2

### Verification

- project-wide searches for `wagtail`, `puput`, `/read/blog/`, and `PUPUT_APPS`
- confirm the inventory includes settings, URLs, dependencies, templates, static assets, and app files

### Done criteria

- every active Wagtail/Puput touchpoint is listed
- there is a concrete edit/delete checklist for phase 2

### Stop gate

Stop after inventory and wait for review.

## Phase 2: Remove Wagtail, Puput, and the Current `blog/` App

### Goal

Completely remove the existing Wagtail/Puput blog implementation before any replacement work begins.

### Primary files to change or delete

- `requirements.txt`
- `igorsimb/settings.py`
- `igorsimb/urls.py`
- `core/templates/core/partials/header.html`
- delete the current `blog/` app directory and all of its contents

### Tasks

- remove `puput`, `wagtail`, `wagtail-markdown`, and any now-unused Wagtail-only packages from `requirements.txt`
- remove `from puput import PUPUT_APPS` from `igorsimb/settings.py`
- remove `INSTALLED_APPS += PUPUT_APPS`
- remove Wagtail middleware from `MIDDLEWARE`
- remove `WAGTAIL_SITE_NAME`, `WAGTAILADMIN_BASE_URL`, and any other Wagtail-only settings
- remove `path("read/", include("puput.urls"))` from `igorsimb/urls.py`
- remove or temporarily disable the current blog nav link in `core/templates/core/partials/header.html`
- delete the current `blog/` directory completely so the replacement starts from a clean slate

### Verification

- `".igorsimb_ru/Scripts/python.exe" manage.py check`
- `git diff -- requirements.txt igorsimb/settings.py igorsimb/urls.py core/templates/core/partials/header.html`

### Done criteria

- no active Wagtail or Puput configuration remains in Django settings or URLs
- the old `blog/` app is fully removed from the repository
- the site still passes `manage.py check` without Wagtail/Puput wiring

### Stop gate

Stop after removal and wait for review.

## Phase 3: Verify Zero Traces Before Rebuild

### Goal

Prove the codebase is Wagtail-free before creating the replacement blog.

### Tasks

- run project-wide searches for `wagtail` and `puput`
- investigate every remaining match in tracked project code
- remove any lingering references in templates, comments, imports, fixtures, or config files if they are still active project artifacts
- confirm there is no active `/read/blog/` usage left in navigation or routing

### Verification

- grep for `wagtail`
- grep for `puput`
- grep for `/read/blog/`
- `".igorsimb_ru/Scripts/python.exe" manage.py check`

### Done criteria

- no active Wagtail or Puput references remain in tracked project files
- no old blog route remains mounted
- the project is in a clean post-Wagtail baseline state

### Stop gate

Stop after zero-trace verification and wait for review. Do not create the new `blog/` app before this review is approved.

## Phase 4: Recreate `blog/` as a Plain Django App

### Goal

Create a fresh `blog` app with no legacy coupling.

### Target files and paths

- new `blog/` app package
- new `blog/migrations/`
- new `blog/templates/blog/`
- new `blog/static/blog/`
- `igorsimb/settings.py`
- `igorsimb/urls.py`

### Tasks

- create a fresh Django app named `blog`
- add the new `blog` app to `INSTALLED_APPS`
- wire public blog URLs at `/blog/`
- create the initial template and static directory structure for the new app
- add placeholder public views/templates so the app is mounted cleanly before the full feature set lands

### Verification

- `".igorsimb_ru/Scripts/python.exe" manage.py check`
- load the new `/blog/` route successfully once implemented

### Done criteria

- a new plain Django `blog` app exists
- routing points at `/blog/`
- there is no Wagtail-era code or directory structure in the recreated app

### Stop gate

Stop after app recreation and wait for review.

## Phase 5: Define the Minimal Blog Domain and Rendering Pipeline

### Goal

Create the smallest durable content model and one Markdown rendering path.

### Expected files

- `blog/models.py`
- `blog/migrations/*.py`
- `blog/forms.py` if needed
- `blog/services.py` or `blog/rendering.py` for centralized Markdown rendering
- `blog/tests.py` or `blog/tests/**`

### Tasks

- define a minimal post model with only fields required for draft and publish flow
- include `title`, `slug`, Markdown body, rendered HTML, status, created timestamp, updated timestamp, and published timestamp
- keep Markdown as the source of truth and rendered HTML as derived content
- create one centralized rendering module used by preview and published output
- ensure rendered code blocks support syntax highlighting cleanly
- choose the safest minimal Markdown behavior for raw HTML handling

### Verification

- model tests for draft/published behavior
- rendering tests for fenced code blocks and common Markdown elements

### Done criteria

- one minimal content model exists
- one rendering path exists
- preview and public rendering can share the same logic

### Stop gate

Stop after model and rendering work and wait for review.

## Phase 6: Build Public Blog Pages

### Goal

Ship the public-facing plain Django blog before the authoring workspace.

### Expected files

- `blog/urls.py`
- `blog/views.py`
- `blog/templates/blog/index.html`
- `blog/templates/blog/detail.html`
- `blog/static/blog/css/*.css`
- `core/templates/core/partials/header.html`

### Tasks

- build the published-post index page at `/blog/`
- build the published-post detail page under `/blog/<slug>/`
- update the site navigation in `core/templates/core/partials/header.html` to point to `/blog/`
- ensure drafts are never publicly accessible
- style typography, code blocks, and images for technical writing readability

### Verification

- view tests for index/detail visibility rules
- manual browser check for `/blog/` and a published post page

### Done criteria

- `/blog/` is the active public blog route
- published posts render correctly
- drafts remain private

### Stop gate

Stop after public pages and wait for review.

## Phase 7: Build the Simple Superuser Authoring Workspace

### Goal

Create a clean, custom, non-admin writing interface optimized for one author.

### Expected files

- `blog/views.py`
- `blog/urls.py`
- `blog/templates/blog/editor.html`
- `blog/templates/blog/dashboard.html`
- `blog/forms.py` if needed
- `blog/static/blog/css/*.css`

### Tasks

- create a superuser-only dashboard for drafts and published posts
- create a superuser-only editor page
- keep the layout focused on title, Markdown body, status, save feedback, preview, and publish action
- use a plain Markdown editing surface rather than a code editor or WYSIWYG system
- keep metadata controls minimal and out of the way

### Verification

- permission tests for anonymous vs superuser access
- manual browser check of dashboard-to-editor flow

### Done criteria

- the author can create and edit drafts in a custom interface
- the interface is simple and writing-first
- Django admin is not the main authoring path

### Stop gate

Stop after the authoring workspace and wait for review.

## Phase 8: Add Datastar-Powered Preview, Autosave, and Publish Actions

### Goal

Make the writing flow feel immediate without turning the page into a heavy SPA.

### Expected files

- `static/js/datastar.js`
- `blog/templates/blog/editor.html`
- `blog/views.py`
- `blog/urls.py`
- supporting templates/partials for preview or status fragments

### Tasks

- add Datastar locally under `static/js/` (already done)
- implement preview refresh from the centralized Markdown renderer
- implement autosave for title/body changes with restrained, debounced updates
- implement clear save-state messaging
- implement publish/unpublish actions through the same interaction model

### Verification

- manual browser check for live preview and autosave behavior
- view tests for preview and publish endpoints where practical

### Done criteria

- preview updates in-place while writing
- autosave reduces save anxiety without noisy UI
- publish state changes cleanly from the editor

### Stop gate

Stop after interactive authoring and wait for review.

## Phase 9: Add Low-Friction Image Insertion

### Goal

Allow image insertion without breaking writing flow.

### Expected files

- `blog/views.py`
- `blog/urls.py`
- `blog/templates/blog/editor.html`
- `blog/static/blog/js/*.js` if a small helper is needed
- media storage configuration already present in `igorsimb/settings.py`

### Tasks

- add a superuser-only upload endpoint
- validate image type and size
- store uploaded images under the project's media storage
- return the uploaded image URL
- support paste and drag-drop insertion into the editor
- insert Markdown image syntax at the cursor automatically

### Verification

- manual browser check for paste/drop flow
- tests for upload permissions and invalid file handling

### Done criteria

- pasted or dropped images upload successfully and insert Markdown automatically
- invalid uploads fail clearly
- the user stays in the editor flow

### Stop gate

Stop after image workflow and wait for review.

## Phase 10: Harden, Test, and Clean Up

### Goal

Verify the end-to-end replacement is stable, clean, and minimal.

### Tasks

- run targeted tests for post lifecycle, permissions, preview consistency, and uploads
- run `manage.py check`
- perform a final grep sweep for `wagtail`, `puput`, and `/read/blog/`
- remove any implementation leftovers created during the replacement work
- update `docs/plans/progress.md` with final status and remaining follow-ups if any

### Verification

- `".igorsimb_ru/Scripts/python.exe" manage.py check`
- `".igorsimb_ru/Scripts/python.exe" manage.py test`
- grep checks for `wagtail`
- grep checks for `puput`
- grep checks for `/read/blog/`

### Done criteria

- the new blog works end-to-end
- the repository contains no active Wagtail/Puput traces
- the new authoring workflow matches the single-author product goal

### Stop gate

Stop after final verification and wait for review.

## Acceptance Criteria

The project is complete only when all of the following are true:

1. Wagtail and Puput are fully removed from dependencies, settings, URLs, templates, and code.
2. The old `blog/` app was deleted before the replacement app was created.
3. A zero-trace verification phase completed before the new `blog` app work began.
4. The replacement uses a plain Django `blog` app with no Wagtail-era abstractions.
5. The public blog lives at `/blog/`.
6. A superuser can create, edit, preview, autosave, and publish posts from a custom writing interface.
7. Public users can view only published posts.
8. Markdown is the source of truth and rendered HTML is derived through one centralized rendering path.
9. Code blocks render well enough for a developer-oriented blog.
10. Datastar is served locally from project static assets and used only for targeted interactivity.
11. Image paste/drag-drop upload works without forcing the author into another screen.
12. No out-of-scope CMS features were added.
