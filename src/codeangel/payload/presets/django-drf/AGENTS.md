# {{area}}/AGENTS.md — Django REST API

<!-- Loaded for any work under {{area}}/. Budget ≤ 50 lines. Detail → {{area}}/docs/ai/, gotchas → {{area}}/docs/learnings/. -->

Python 3.12 · Django · Django REST Framework · drf-spectacular (OpenAPI) · pytest + pytest-django · ruff · prek · poetry. Run every command from `{{area}}/` via `poetry run …`.

## Router
| when | read |
|---|---|
| env setup; running tests, lint, migrations, server, management commands | `{{area}}/docs/ai/commands.md` |
| where code goes, request path, live routes, exemplar files | `{{area}}/docs/ai/architecture.md` |
| writing views, serializers, services, models, admin, migrations; style | `{{area}}/docs/ai/conventions.md` |
| writing / fixing tests | `{{area}}/docs/ai/testing.md` |
| gathering proof a change works: start, seed, auth, API transcript, screenshot | `{{area}}/docs/ai/evidence.md` |
| DRF behaviour: status codes, auth, errors, pagination | `{{area}}/docs/learnings/api.md` |
| touching `{{area}}/<app>/` | `{{area}}/docs/learnings/domain/<app>.md` (if it exists) |
| poetry, prek, ruff, env trouble | `{{area}}/docs/learnings/tooling.md` |
| every {{area_name}} learnings file | `{{area}}/docs/learnings/README.md` |

## Always
- Apps = business domains, not entities. New code follows the exemplar named in `{{area}}/docs/ai/architecture.md` (urls → view → serializer → service → model, with tests).
- Views stay thin; business rules live in services. Client errors raise DRF exceptions (`ValidationError` 400, `NotFound` 404, `PermissionDenied` 403) — never let `ValueError` / `IntegrityError` / `ObjectDoesNotExist` / `KeyError` escape as a 500.
- Permissions are explicit: the default is `IsAuthenticated`; a public endpoint sets `permission_classes = [AllowAny]` with a comment saying why. Scope `get_queryset()` to the requesting user.
- Migrations: `makemigrations <app> --name <desc>` only — never bare; never edit existing migration files.
- Tests never hit paid or external APIs — mock them.
- Modular monolith: no new services, queues, caches, or infra without a ticket. No absolute paths (`settings.BASE_DIR`).
- Added / removed a route → update the route table in `{{area}}/docs/ai/architecture.md`.

## Done — gates, relative to the base commit
1. Lint / format: `poetry run prek run --files <changed files>` exit 0 — changed files fully clean, incl. old findings in them.
2. Schema drift: `poetry run python manage.py makemigrations --check --dry-run` — no new drift; every app whose models changed has its migration.
3. Tests: `poetry run pytest -q` collects + runs; no failure that didn't fail on the base; new tests pass.
4. New / changed behaviour tested per `{{area}}/docs/ai/testing.md`.
