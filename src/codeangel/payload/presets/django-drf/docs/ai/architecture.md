# {{area_name}} architecture

<!-- When: deciding where code goes, tracing a request, finding an exemplar, checking live routes. -->

## Layout (`{{area}}/`)
```
{{package}}/       settings · urls (/admin/, /api/schema/, /api/docs/, app routes under /api/) · asgi · wsgi
core/              models.BaseModel (abstract created_at / updated_at) · base_test.BaseTest
<app>/             one Django app per business domain (none yet)
docs/ai/, docs/learnings/   agent docs
```
Apps = business domains, not entities: a new entity joins the existing app of its domain.

## Request path
`{{area}}/{{package}}/urls.py` `path("api/<prefix>/", include("<app>.urls"))` → `<app>/urls.py` (a DRF `DefaultRouter` registering ViewSets, or `path()` for single APIViews) → view `<app>/views.py` → serializer `<app>/serializers.py` (input validation + representation) → service `<app>/services.py` (business rules, transactions) → models / QuerySets.

## Per-app file pattern
| file | holds |
|---|---|
| `models.py` | models, subclassing `core.models.BaseModel` |
| `choices.py` | `models.TextChoices` |
| `querysets.py` | custom Managers / QuerySets — read logic (no selector layer) |
| `admin.py` | admin for every model |
| `serializers.py` | `<Res>Serializer` (read), `<Res>CreateSerializer` / `<Res>UpdateSerializer` when write shapes differ |
| `views.py` | ViewSets / APIViews; thin |
| `urls.py` | the app's router; included under `api/<prefix>/` |
| `permissions.py` | custom permission classes |
| `services.py` | business ops `get_<x>`, `create_<x>`, …; `@transaction.atomic` for multi-write |
| `management/commands/<cmd>.py` | backfills / one-offs |
| `tests/base.py` · `tests/test_<res>_api.py` | shared fixtures · `Test<Res><Action>` classes |
A file past ~300 lines becomes a package (`views/<res>.py`, …) with the same names re-exported.

Exemplar — copy its shape: none yet. The first app built through the build loop becomes the exemplar; list its urls, view, serializer, service, and test files here.

## Live routes
Update on every add / remove. Regenerate from `{{area}}/`: `poetry run python manage.py spectacular` and read `paths:`.
```
GET  /api/schema/   public   OpenAPI document (drf-spectacular)
GET  /api/docs/     public   Swagger UI
```
Pagination = `LimitOffsetPagination` (settings): `?limit=&offset=` → `{"count", "next", "previous", "results"}`.
Auth = `SessionAuthentication` (settings) with a default `IsAuthenticated` permission. Unauthenticated requests get **403** (no `WWW-Authenticate` header, so DRF can't send 401) — a token / JWT class listed first in `DEFAULT_AUTHENTICATION_CLASSES` switches that to 401. A mobile client needs one; adding it is a ticket-level decision.
