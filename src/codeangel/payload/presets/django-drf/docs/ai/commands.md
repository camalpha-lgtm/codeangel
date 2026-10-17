# {{area_name}} commands

<!-- When: setting up an env, running tests / lint / migrations / server / management commands. cwd = {{area}}/. -->

## Setup — fresh clone or new worktree (each worktree needs its own venv)
1. `poetry env use <python3.12 exe>` — Windows: `py -3.12 -c "import sys;print(sys.executable)"`
2. `poetry install`
3. Health: `poetry run python manage.py check`

## Daily
| purpose | command |
|---|---|
| all tests | `poetry run pytest -q` |
| one test | `poetry run pytest <app>/tests/<file>.py::<Class>::<test> -q` |
| lint changed files | `poetry run prek run --files <paths relative to {{area}}/>` |
| lint everything | `poetry run prek run --all-files` (auto-fixes; rerun until exit 0) |
| lint debt, read-only | `poetry run ruff check --output-format concise .` (same ruff as the prek hooks) |
| schema drift | `poetry run python manage.py makemigrations --check --dry-run [<app>]` |
| new migration | `poetry run python manage.py makemigrations <app> --name <snake_desc>` |
| new app | `poetry run python manage.py startapp <name>` → add to `INSTALLED_APPS` → add `<app>/urls.py` → `path("api/<prefix>/", include("<app>.urls"))` in `{{area}}/{{package}}/urls.py` |
| server | `poetry run python manage.py runserver` → Swagger UI `/api/docs/`, OpenAPI `/api/schema/` |
| OpenAPI dump | `poetry run python manage.py spectacular` (YAML to stdout; add `--validate --fail-on-warn` to lint the schema) |
| add dependency | `poetry add <pkg>` — never hand-edit `poetry.lock` |

## Environment variables (read in `{{area}}/{{package}}/settings.py`)
| name | default | purpose |
|---|---|---|
| `DJANGO_SECRET_KEY` | dev placeholder | set in any shared / production environment |
| `DEBUG` | `true` | `true` / `false` |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | comma-separated |

## prek hooks (`{{area}}/.pre-commit-config.yaml`)
whitespace · EOF · yaml / toml / json · merge-conflict · debug-statements · `ruff check --fix` · `ruff format` · `manage.py check`. Sees only files under `{{area}}/`. `manage.py check` does NOT catch schema drift → run the drift check too.

## Management commands
| command | does | needs |
|---|---|---|
<!-- one row per custom command; paid or data-mutating ones say so -->
