# Repository Guidelines

## Project Structure & Module Organization

This is a Django 5.1 portfolio site. `igorsimb/` contains project settings, root URLs, sitemap configuration, and ASGI/WSGI entry points. Feature apps live at the repository root: `core/` serves the portfolio pages, `blog/` implements publishing and its editor, `accounts/` provides the custom user model, and `store/` plus `store_users/` contain shop functionality. Keep app-specific templates and assets under `<app>/templates/<app>/` and `<app>/static/<app>/`. Shared assets are in `static/`, translations in `locale/`, uploaded files in the ignored `media/`, and design notes in `docs/plans/`.

## Build, Test, and Development Commands

Use the local Windows virtual environment when available:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe manage.py migrate
.venv\Scripts\python.exe manage.py runserver
.venv\Scripts\python.exe manage.py test
```

The first command installs dependencies; the others prepare the database, start the local server, and run all Django tests. Run one app with `manage.py test blog`. Before running Django commands, create a local `.env` containing the settings required by `igorsimb/settings.py`, including `DJANGO_SECRET_KEY`, mail values, and `LOCAL_DEVELOPMENT=True` for SQLite. Never commit `.env`, databases, or uploaded media.

## Coding Style & Naming Conventions

Follow PEP 8 with four-space indentation and keep new lines near 120 characters or fewer. Use `snake_case` for functions and modules, `PascalCase` for models, forms, views, and test classes, and descriptive Django URL names grouped by app namespace. Reuse existing class-based views, forms, template partials, and theme-aware Bootstrap patterns. No formatter or linter is configured, so keep edits focused and match surrounding code.

## Testing Guidelines

Tests use Django's `TestCase` and live in each app's `tests.py`. For future tests use pytest. Name methods `test_<observable_behavior>` and classes after the unit or page under test, such as `BlogPublicViewTests`. Cover model rules, permissions, redirects, templates, and response content at the narrowest useful layer. Run the affected app first, then the full suite before opening a pull request.

## Commit & Pull Request Guidelines

History follows Conventional Commits, commonly `feat(scope): ...`, `fix(scope): ...`, and `chore: ...`. Write concise, imperative subjects, for example `fix(blog): reject invalid image uploads`. Pull requests should explain the user-visible outcome, identify migrations or configuration changes, link relevant issues, and include screenshots for template or styling changes. Report the test commands run and avoid bundling unrelated refactors.
