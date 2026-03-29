# Blog Rework Planning Progress

## Current Task

Rewrite `docs/plans/blog-rework.md` so it matches the real project structure and the required sequencing:

1. inventory Wagtail usage
2. remove Wagtail completely
3. verify zero traces remain
4. only then start the new blog implementation plan

## Progress Log

- Inspected the current project layout and confirmed there is no `AGENTS.md` file in the repository.
- Identified current Wagtail and Puput coupling in `igorsimb/settings.py`, `igorsimb/urls.py`, `requirements.txt`, `blog/templates/puput/**`, and `core/templates/core/partials/header.html`.
- Confirmed the Python `blog` app code is currently minimal (`blog/models.py`, `blog/views.py`, `blog/apps.py`) while the active blog behavior is coming from Puput/Wagtail integration.
- Verified the global instructions file is provided outside the repo and used its phase-based review requirement when rewriting the plan.
- Confirmed current runtime still passes `".igorsimb_ru/Scripts/python.exe" manage.py check` before any implementation work.
- Rewrote `docs/plans/blog-rework.md` into a project-specific phased plan with real file paths, hard review gates after every phase, Wagtail-first removal sequencing, zero-trace verification before rebuild, `/blog/` as the new public route, local Datastar delivery, and a simple single-author writing workflow.

## Current Status

- Planning task complete.
- Awaiting user review of `docs/plans/blog-rework.md` before any implementation phase begins.

## Phase 1 Inventory

### Active Wagtail and Puput touchpoints

- `requirements.txt`
  - direct blog platform dependencies:
    - `puput==2.1.1`
    - `wagtail==6.2.2`
    - `wagtail-markdown==0.11.1`
  - likely Wagtail-adjacent cleanup candidates with no tracked project imports found during Phase 1:
    - `django-modelcluster==6.3`
    - `django-taggit==5.0.1`
    - `django-treebeard==4.7.1`
    - `draftjs-exporter==5.0.0`
    - `telepath==0.3.1`
- `igorsimb/settings.py`
  - `from puput import PUPUT_APPS`
  - `INSTALLED_APPS += PUPUT_APPS`
  - `wagtail.contrib.redirects.middleware.RedirectMiddleware`
  - `WAGTAIL_SITE_NAME`
  - `WAGTAILADMIN_BASE_URL`
- `igorsimb/urls.py`
  - `path("read/", include("puput.urls"))`
  - adjacent comment referencing `blog/templates/puput/base.html`
- `core/templates/core/partials/header.html`
  - navigation link currently points to `/read/blog/`
- `blog/`
  - entire app is slated for deletion before recreation
  - active Puput template tree:
    - `blog/templates/puput/base.html`
    - `blog/templates/puput/base_backup.html`
    - `blog/templates/puput/blog_page.html`
    - `blog/templates/puput/entry_page.html`
    - `blog/templates/puput/entry_page_header.html`
    - `blog/templates/puput/entry_links.html`
    - `blog/templates/puput/related_entries.html`
    - `blog/templates/puput/share_links.html`
    - `blog/templates/puput/comments/django_comments.html`
    - `blog/templates/puput/comments/disqus.html`
    - `blog/templates/puput/tags/archives_list.html`
    - `blog/templates/puput/tags/categories_list.html`
    - `blog/templates/puput/tags/entries_list.html`
    - `blog/templates/puput/tags/tags_list.html`
  - blog app files to remove as part of the clean reset:
    - `blog/__init__.py`
    - `blog/admin.py`
    - `blog/apps.py`
    - `blog/models.py`
    - `blog/views.py`
    - `blog/tests.py`
    - `blog/migrations/__init__.py`
  - blog-specific static assets to remove with the app:
    - `blog/static/css/custom_blog.css`
    - `blog/static/css/main_nav_blog.css`

### Non-blog findings

- No non-blog Python or template files were found to import or load Wagtail or Puput directly beyond the shared nav link in `core/templates/core/partials/header.html`.
- `django_quill` is used by the store app and is not part of the Wagtail removal scope:
  - `igorsimb/settings.py`
  - `store/models.py`
  - `store/migrations/0001_initial.py`

### Phase 2 deletion map

- Edit `requirements.txt` to remove direct Wagtail/Puput dependencies and review the Wagtail-adjacent package removals listed above.
- Edit `igorsimb/settings.py` to remove Puput import, `PUPUT_APPS`, Wagtail middleware, and Wagtail settings.
- Edit `igorsimb/urls.py` to remove the Puput route and its stale comment.
- Edit `core/templates/core/partials/header.html` to remove or temporarily disable the current blog nav until the new `/blog/` route exists.
- Delete the current `blog/` app directory completely before recreating it later.

### Reminder

- After Phase 3 completes and zero-trace verification passes, remind the user to deploy the blog-less version to the server before Phase 4 begins.

### Phase 1 verification notes

- Searched tracked project code for `wagtail`, `puput`, `PUPUT_APPS`, and `/read/blog/`.
- Confirmed Wagtail/Puput coupling is concentrated in `requirements.txt`, `igorsimb/settings.py`, `igorsimb/urls.py`, `core/templates/core/partials/header.html`, and the current `blog/` app.

## Phase 2 Removal

### Changes completed

- Removed Wagtail/Puput dependencies and Wagtail-adjacent cleanup candidates from `requirements.txt`:
  - `django-modelcluster`
  - `django-taggit`
  - `django-treebeard`
  - `draftjs-exporter`
  - `puput`
  - `telepath`
  - `wagtail`
  - `wagtail-markdown`
- Removed Puput and Wagtail wiring from `igorsimb/settings.py`:
  - deleted `from puput import PUPUT_APPS`
  - removed `blog` from `INSTALLED_APPS`
  - removed `INSTALLED_APPS += PUPUT_APPS`
  - removed `wagtail.contrib.redirects.middleware.RedirectMiddleware`
  - removed `WAGTAIL_SITE_NAME`
  - removed `WAGTAILADMIN_BASE_URL`
- Removed the Puput route from `igorsimb/urls.py`.
- Removed the old blog navigation link from `core/templates/core/partials/header.html`.
- Deleted the tracked contents of the current `blog/` app so the replacement can later start from a clean slate.

### Verification

- `".igorsimb_ru/Scripts/python.exe" manage.py check`
- Result: `System check identified no issues (0 silenced).`

### Notes

- The tracked `blog/` app files are deleted.
- Local generated cache files under `blog/__pycache__/` and `blog/migrations/__pycache__/` may still exist in the working tree, but they are not active source files and are not part of the replacement plan.
- Phase 3 will verify zero active `wagtail`, `puput`, and `/read/blog/` traces remain in tracked project files.

## Phase 3 Zero-Trace Verification

### Verification completed

- Searched tracked `*.py` files for `wagtail`, `puput`, `PUPUT_APPS`, and `/read/blog/`.
- Searched tracked `*.html` files for `wagtail`, `puput`, and `/read/blog/`.
- Searched `requirements.txt` for `wagtail`, `puput`, and `/read/blog/`.
- Ran `".igorsimb_ru/Scripts/python.exe" manage.py check`.

### Results

- No active `wagtail`, `puput`, `PUPUT_APPS`, or `/read/blog/` references remain in tracked Python, HTML, or dependency files.
- Remaining search hits exist only in planning documents under `docs/plans/`, which is expected and does not affect runtime.
- `manage.py check` still passes in the blog-less state.

### Deployment reminder

- Before Phase 4 begins, remind the user to deploy this blog-less version to the server on reg.ru and verify it there before recreating the `blog` app.

### Remote deploy notes for the Phase 3 state

- No `makemigrations` is needed for this phase.
- No `migrate` is needed for this phase because no new migrations were created or changed.
- The remote server does need the updated Python dependencies installed after `git pull`, because `requirements.txt` changed.
- Suggested remote sequence for this phase:
  - SSH into the server
  - `git pull`
  - install updated requirements in the server venv
  - optionally run `manage.py check`
  - upload `.app-restart` to trigger restart
