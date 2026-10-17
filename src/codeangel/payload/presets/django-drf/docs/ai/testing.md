# {{area_name}} testing

<!-- When: writing or fixing tests. Gotchas: {{area}}/docs/learnings/api.md. -->

- Location: `<app>/tests/test_<res>_api.py`; shared fixtures in `<app>/tests/base.py`; cross-cutting tests in `core/tests/`.
- Class-based: inherit `core.base_test.BaseTest` (gives `self.client` = DRF `APIClient`, plus `django_db`) or an app `Base*Test`; one `Test<Res><Action>` class per endpoint action; methods `test_<behaviour>`.
- Fixtures: `@pytest.fixture` methods with typed returns; create every row a test needs explicitly.
- Requests: real URLs (`/api/...`); JSON bodies via `self.client.post(url, data, format="json")`; auth via `self.client.force_authenticate(user=user)` (skips the authentication classes; see `{{area}}/docs/learnings/api.md`).
- Assert in order: `status_code` → `response.json()` (paginated: `["results"]`, `["count"]`) → DB state (`refresh_from_db()` / queries).
- Per endpoint cover: happy path · unauthenticated (403 with session auth, 401 with token auth) · 404 missing object · 400 invalid input (`{"field": ["message"]}`) · isolation from other users' data (their objects 404).
- An unhandled exception in a view re-raises inside the test (the Django test client re-raises) — read the bottom of the traceback; fix the service, not the test.
- Mock every paid / external / network call.
- Run one: `poetry run pytest <test id> -q`; all: `poetry run pytest -q`. Zero collected tests exits 5 — keep at least the core smoke test.
