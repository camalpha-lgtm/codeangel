# {{area_name}} conventions

<!-- When: writing or reviewing views, serializers, services, models, admin, migrations, or style. -->

## API
- Views: prefer `ModelViewSet` / `GenericViewSet` + mixins for CRUD, `APIView` for one-off actions. Declare `serializer_class`, and `permission_classes` whenever they differ from the defaults. No business logic in views — call a service for writes.
- Scope data to the caller in `get_queryset()` (e.g. `.filter(owner=self.request.user)`); that also makes other users' objects 404. Put `select_related` / `prefetch_related` there too (no N+1).
- Routes: `<app>/urls.py` registers ViewSets on a `DefaultRouter`; mount it in `{{area}}/{{package}}/urls.py` under `api/<prefix>/`. Trailing slashes everywhere.
- Serializers: validate input shape (`validate_<field>`, `validate`) in the serializer; business rules in services. `read_only_fields` / `extra_kwargs` instead of ad-hoc field blocking. Nested writes go through a service, not `serializer.save()` magic.
- Documentation: `@extend_schema` (drf-spectacular) on views whose request / response isn't obvious from the serializer.

## Services
- Plain functions taking model instances + validated data; return a model.
- Client errors → raise `rest_framework.exceptions` (`ValidationError` 400, `NotFound` 404, `PermissionDenied` 403); use `get_object_or_404` / catch `DoesNotExist` → `NotFound` (`raise … from e`).
- PATCH: `partial=True`; apply only provided fields; `save(update_fields=[...])`.
- Multi-write → `@transaction.atomic`.

## Models
- Subclass `core.models.BaseModel`; enums in `<app>/choices.py`.
- `Meta.constraints` with explicit `name=`; FKs set `related_name`; define `__str__` (ruff DJ008).

## Admin
Register every model; `list_select_related` for FK columns; search / filter on the fields staff look up.

## Migrations
Generate per app with a name (`makemigrations <app> --name <desc>`), read the `--dry-run` first; never hand-write; never edit existing files unless the ticket says so; commit with the model change.

## Style
- ruff rules E, F, I, B, UP, DJ; line 100; double quotes; py312 syntax (`X | None`, `list[str]`).
- Type-hint every function; `raise … from e` inside `except`; absolute imports from the app root.
- Config via env (`{{area}}/docs/ai/commands.md` → Environment variables); no absolute or machine-specific paths. The schema / docs endpoints are public by default — set `SPECTACULAR_SETTINGS["SERVE_PERMISSIONS"]` before exposing a production deployment.
