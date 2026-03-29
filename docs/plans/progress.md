# Blog Rework Planning Progress

## Current Task

Complete Phase 10 hardening, cleanup, and final verification for the rebuilt blog app.

## Progress Log

- Inspected the current project layout and confirmed there is no `AGENTS.md` file in the repository.
- Identified current Wagtail and Puput coupling in `igorsimb/settings.py`, `igorsimb/urls.py`, `requirements.txt`, `blog/templates/puput/**`, and `core/templates/core/partials/header.html`.
- Confirmed the Python `blog` app code is currently minimal (`blog/models.py`, `blog/views.py`, `blog/apps.py`) while the active blog behavior is coming from Puput/Wagtail integration.
- Verified the global instructions file is provided outside the repo and used its phase-based review requirement when rewriting the plan.
- Confirmed current runtime still passes `".igorsimb_ru/Scripts/python.exe" manage.py check` before any implementation work.
- Rewrote `docs/plans/blog-rework.md` into a project-specific phased plan with real file paths, hard review gates after every phase, Wagtail-first removal sequencing, zero-trace verification before rebuild, `/blog/` as the new public route, local Datastar delivery, and a simple single-author writing workflow.

## Current Status

- Phases 1 through 8 are complete.
- Phase 8 follow-up UI cleanup is also complete and verified.
- Phase 9 image upload and insertion is now complete and verified.
- Phase 10 final verification and cleanup is now complete.
- The rebuilt plain Django `blog` app is live in the codebase with the Datastar-powered editor workflow.
- The blog rebuild plan is complete; any next session can start from follow-up polish or deployment needs.

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

## Phase 4 Plain Django App Recreation

### Changes completed

- Recreated `blog/` as a fresh plain Django app with new tracked source files:
  - `blog/__init__.py`
  - `blog/apps.py`
  - `blog/models.py`
  - `blog/views.py`
  - `blog/urls.py`
  - `blog/migrations/__init__.py`
- Added the new app to `INSTALLED_APPS` in `igorsimb/settings.py`.
- Mounted the new public route at `/blog/` in `igorsimb/urls.py`.
- Added a placeholder public page in `blog/templates/blog/index.html`.
- Added initial app-specific static styling in `blog/static/blog/css/blog.css`.
- Restored a blog navigation link in `core/templates/core/partials/header.html` pointing to the new `/blog/` route.

### Verification completed

- Ran `".igorsimb_ru/Scripts/python.exe" manage.py check`.
- Resolved `reverse("blog:index")` and confirmed it returns `/blog/`.

### Results

- The new plain Django `blog` app is installed and mounted cleanly.
- The placeholder public page is reachable at `/blog/`.
- `manage.py check` passes after recreating the app.

## Phase 5 Minimal Domain And Rendering

### Changes completed

- Added a minimal `Post` model in `blog/models.py` with:
  - `title`
  - `slug`
  - `markdown_body`
  - `rendered_html`
  - `status`
  - `created_at`
  - `updated_at`
  - `published_at`
- Kept Markdown as the source of truth and derived `rendered_html` during `Post.save()`.
- Added `blog/rendering.py` as the single centralized Markdown rendering path.
- Configured Markdown rendering with fenced code blocks and syntax-highlighting-friendly HTML.
- Sanitized rendered HTML with `bleach` so raw HTML from Markdown input is not trusted as-is.
- Added `blog/tests.py` for draft/published state behavior and Markdown rendering behavior.
- Added the initial `blog/migrations/0001_initial.py` migration for the new model.

### Verification completed

- Ran `".igorsimb_ru/Scripts/python.exe" manage.py test blog`.
- Ran `".igorsimb_ru/Scripts/python.exe" manage.py check`.

### Results

- Draft and published state behavior is covered by model tests.
- Common Markdown elements and fenced code blocks are covered by rendering tests.
- Raw HTML input is escaped before Markdown conversion and the rendered output is sanitized.
- Phase 5 verification passes cleanly.

## Phase 6 Public Blog Pages

### Changes completed

- Replaced the Phase 4 placeholder with a real published-post index at `blog/templates/blog/index.html`.
- Added a published-post detail template at `blog/templates/blog/detail.html`.
- Updated `blog/views.py` to use published-only querysets for both public index and detail views.
- Added the `/blog/<slug>/` route in `blog/urls.py`.
- Expanded `blog/static/blog/css/blog.css` to style public post lists, technical typography, code blocks, and images.
- Updated the header nav active state so it stays highlighted on both `/blog/` and `/blog/<slug>/`.
- Added public visibility tests to `blog/tests.py` for published list/detail access and draft 404 behavior.

### Verification completed

- Ran `".igorsimb_ru/Scripts/python.exe" manage.py test blog`.
- Ran `".igorsimb_ru/Scripts/python.exe" manage.py check`.

### Results

- Public view tests confirm the index lists published posts only.
- Public view tests confirm published detail pages are reachable.
- Public view tests confirm draft posts return 404 and remain private.
- Phase 6 verification passes cleanly.

## Phase 7 Superuser Authoring Workspace

### Changes completed

- Added `blog/forms.py` with a minimal `PostEditorForm` for title and Markdown body.
- Added a superuser-only dashboard in `blog/templates/blog/dashboard.html`.
- Added a superuser-only editor in `blog/templates/blog/editor.html`.
- Added `/blog/dashboard/`, `/blog/write/`, and `/blog/write/<pk>/` routes.
- Added simple save, publish, and unpublish actions without using Django admin as the main workflow.
- Reused the centralized Markdown renderer for the editor preview.
- Added workspace styling to `blog/static/blog/css/blog.css`.
- Added authoring access and workflow tests to `blog/tests.py`.

### Verification completed

- Ran `".igorsimb_ru/Scripts/python.exe" manage.py test blog`.
- Ran `".igorsimb_ru/Scripts/python.exe" manage.py check`.

### Results

- Anonymous users are redirected away from the authoring workspace.
- Authenticated non-superusers receive `403` for the authoring workspace.
- Superusers can open the dashboard, save drafts, and publish posts through the custom editor.
- Automated Phase 7 verification passes cleanly.
- Manual browser verification of the dashboard/editor flow is still pending.

### Reviewer follow-up

- Reserved workspace slugs are now blocked during slug generation for new posts.
- Editor object loading now happens after permission checks instead of before them.
- Dashboard and editor setup-state handling now fail soft when the blog table is unavailable.
- Added broader protected-route coverage for anonymous and non-superuser GET/POST access.
- Re-ran reviewer checks after the fixes; no remaining code-level findings were reported.

## Phase 8 Datastar Interactivity

### Changes completed

- Added Datastar to the editor page from the local `static/js/datastar.js` asset.
- Added a three-way editor layout switch: `Editor`, `Editor and Preview`, and `Preview`.
- Added a sidebar toggle to free more writing space while editing.
- Expanded the editor workspace width and writing surface height for a roomier authoring flow.
- Added a Datastar-powered preview endpoint using the centralized Markdown renderer.
- Added a Datastar-powered save endpoint for autosave, explicit save, publish, and unpublish actions.
- Updated the editor to patch preview HTML, save-state messaging, slug/status metadata, and editor URL from JSON responses.
- Kept the existing server-rendered submit/message flow working as a non-JavaScript fallback.
- Added Phase 8 endpoint tests for preview, autosave, publish, unpublish, and access control.

### Verification completed

- Ran `".igorsimb_ru/Scripts/python.exe" manage.py test blog`.
- Ran `".igorsimb_ru/Scripts/python.exe" manage.py check`.

### Results

- Datastar preview/save endpoints pass automated coverage.
- Autosave, publish, and unpublish actions return updated editor state cleanly.
- Existing non-JavaScript editor flow still passes the earlier authoring tests.
- Phase 8 automated verification passes cleanly.

## Phase 8 Follow-up Polish

### Changes completed

- Fixed Datastar loading in `blog/templates/blog/editor.html` by switching the local `static/js/datastar.js` include to `type="module"`.
- Fixed the editor mode switch active-state binding by changing from `data-class:...` usage to Datastar object syntax in `blog/templates/blog/editor.html`.
- Updated the editor heading and preview title to react to the current typed title instead of showing stale placeholder text.
- Reduced editor UI noise in `blog/templates/blog/editor.html` by removing redundant helper copy and the idle status text.
- Updated editor save-status timestamps in `blog/views.py` to use Django local time so they render in Moscow time.
- Reduced excessive top spacing across the blog pages in `blog/static/blog/css/blog.css`.
- Moved the editor mode switch into the metadata row and converted it to a compact icon-only control.
- Kept the sidebar toggle and three-mode editor workflow while making the active state more visually obvious.

### Verification completed

- Ran `".igorsimb_ru/Scripts/python.exe" manage.py test blog`.
- Ran `".igorsimb_ru/Scripts/python.exe" manage.py check`.
- Verified in the browser that the editor mode switch active state now renders correctly.
- Verified in the browser that the reduced top spacing feels better on the blog pages.

### Results

- The editor now feels lighter and more writing-focused without losing the Phase 8 functionality.
- The Datastar integration works correctly with the local module build.
- Timestamps shown by the editor now respect the configured Moscow timezone.
- The current handoff point is ready for Phase 9 planning and implementation.

### Important operational notes

- If the production server shows the same stale migration-history issue for app `blog`, do not drop the database.
- Repair it by removing only the stale `django_migrations` rows for `app='blog'`, then rerun `migrate blog`.
- A separate admin issue was traced to a repo-local `static/admin/` override; that directory was removed manually by the user.

## Phase 9 Low-Friction Image Insertion

### Changes completed

- Added a superuser-only image upload endpoint in `blog/views.py` and mounted it at `blog:editor_upload_image` in `blog/urls.py`.
- Validated upload presence, content type, file size, and actual image bytes before saving uploaded files.
- Stored uploaded editor images under `MEDIA_ROOT/blog/images/%Y/%m/` with normalized filenames and content-type-based extensions.
- Returned the uploaded file URL in a minimal JSON response shape for the editor helper.
- Added a small editor-only helper script at `blog/static/blog/js/editor-images.js` for paste and drag-drop upload flow.
- Wired the existing editor in `blog/templates/blog/editor.html` to use the upload helper without adding a separate media UI.
- Inserted standard Markdown image syntax at the current cursor after each successful upload.
- Added a temporary drag-over state in `blog/static/blog/css/blog.css` so drop targeting is clearer while writing.
- Added upload tests in `blog/tests.py` for success, anonymous redirect, non-superuser `403`, invalid content type, oversized files, and invalid image bytes.

### Verification completed

- Ran `".igorsimb_ru/Scripts/python.exe" manage.py test blog`.
- Ran `".igorsimb_ru/Scripts/python.exe" manage.py check`.

### Results

- The editor now supports image paste and drag-drop upload without leaving the writing view.
- Invalid uploads return clear JSON errors and do not create files.
- The non-JavaScript editor flow remains intact because upload support is additive and editor-local.
- Manual browser verification of the paste/drop flow is still pending.

### Phase 9 follow-up hardening

- Added explicit handling for Pillow `DecompressionBombError` in `blog/views.py` so oversized-dimension image attacks return a clear `400` JSON error instead of a server error.
- Added a regression test in `blog/tests.py` covering the decompression-bomb validation path.
- Re-ran `".igorsimb_ru/Scripts/python.exe" manage.py test blog` and `".igorsimb_ru/Scripts/python.exe" manage.py check` after the hardening change.

## Phase 10 Harden, Test, And Clean Up

### Changes completed

- Fixed stale `core/tests.py` homepage tests so they exercise the actual current `core:main` route and template instead of the store root route.
- Switched heavy blog test setup in `blog/tests.py` from per-test user creation to `setUpTestData()` so password hashing is not repeated dozens of times.
- Removed noisy debug `print()` statements from `store/utils.py` that were polluting test output.
- Kept the Phase 9 renderer and upload hardening in place as part of the final verified state.

### Verification completed

- Ran `".igorsimb_ru/Scripts/python.exe" manage.py test`.
- Ran `".igorsimb_ru/Scripts/python.exe" manage.py check`.
- Ran content searches for `wagtail`, `puput`, and `/read/blog/`.

### Results

- The full Django test suite now passes: 55 tests, 0 failures.
- `manage.py check` passes cleanly.
- Repeated `manage.py test blog --keepdb` runs dropped from about 25 seconds to about 3 seconds wall time after the test setup cleanup; the main slowdown was repeated password hashing in test setup, not the blog runtime code.
- Remaining `wagtail`, `puput`, and `/read/blog/` matches exist only in planning documents under `docs/plans/`; no active runtime code references remain.

## Final Review Follow-up

### Changes completed

- Added a small shared template tag in `core/templatetags/navigation.py` so the language switcher preserves the correct current path for both i18n-prefixed pages and unprefixed routes like `/blog/`.
- Updated `core/templates/core/partials/header.html` to use the new language-switch path helper instead of slicing the URL blindly.
- Tightened `blog/views.py` image upload validation so the decoded Pillow image format must match the claimed allowed content type before the file is accepted.
- Switched blog image storage path suffix selection to use the validated decoded image content type.
- Added regression coverage in `core/tests.py` and `blog/tests.py` for language-switch hidden `next` values and mismatched image-format uploads.

### Verification completed

- Confirmed manual testing covered the image upload workflow and preview behavior.
- Ran `".igorsimb_ru/Scripts/python.exe" manage.py test`.
- Ran `".igorsimb_ru/Scripts/python.exe" manage.py check`.

### Results

- Switching languages from `/blog/` now keeps the user on the blog page instead of generating a broken redirect path.
- Blog image uploads now validate the actual decoded image format, not just the reported request MIME type.
- The full test suite now passes with 58 tests.
