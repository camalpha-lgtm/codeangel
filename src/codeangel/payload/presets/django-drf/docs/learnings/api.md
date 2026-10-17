# {{area_name}} API (Django REST Framework)

<!-- When: DRF status codes, authentication, error handling, pagination, or API tests behaving unexpectedly. -->

- **Unauthenticated requests under `SessionAuthentication` return 403, not 401.** — a 401 needs a `WWW-Authenticate` header, and session auth defines none. With `BasicAuthentication` first the same request returns 401 + `WWW-Authenticate: Basic realm="api"`; a token / JWT class first behaves the same. Write tests (and client error handling) for the auth class actually in `DEFAULT_AUTHENTICATION_CLASSES`. src: codeangel seed, verified in a generated project
- **Only `APIException` subclasses, `Http404`, and Django's `PermissionDenied` become responses; any other exception (`Model.DoesNotExist`, `IntegrityError`, `ValueError`, `KeyError`) is a 500.** — use `get_object_or_404` (→ 404 `{"detail": "No <Model> matches the given query."}`) or catch and raise `NotFound` / `ValidationError`. src: codeangel seed, verified
- **The Django test client re-raises an unhandled view exception inside the test, while the served response is 500.** — pytest shows a traceback instead of a 500; `APIClient(raise_request_exception=False)` reproduces what a client would see. src: codeangel seed, verified
- **Serializer validation errors are 400 with a body keyed by field: `{"name": ["This field may not be blank."]}`** — not 422. Non-field errors sit under `non_field_errors`. src: codeangel seed, verified
- **`LimitOffsetPagination` (the project default) takes `?limit=&offset=` and returns `{"count", "next", "previous", "results"}`.** — tests read `response.json()["results"]`. src: codeangel seed, verified
- **`APIClient.force_authenticate(user=…)` authenticates a request without running any authentication class.** — it exercises permissions and queryset scoping, not login; test the login path separately. src: codeangel seed, verified
