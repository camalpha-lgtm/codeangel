# {{area_name}} evidence

<!-- When: gathering proof that a change works (build-loop VERIFY, check V9) or running the API by hand to show a behaviour. cwd = {{area}}/; POSIX shell (Git Bash on Windows). -->

Recipe: start → seed → auth → capture. Artefacts go to `docs/specs/evidence/<TICKET>/` at the repo root (`../docs/specs/evidence/<TICKET>/` from `{{area}}/`); name them `ac-<n>-api.txt` / `ac-<n>-ui.png` (plus `ac-<n>-ui.mp4` and a small `ac-<n>-ui.gif` preview for a flow). Create the directory with `T evidence <TICKET>` (git-ignored; build-review publishes the screenshots and videos to the branch `evidence/<TICKET>` and shows them in the PR). Never commit credentials.

## 1. Start on throwaway data
| step | command |
|---|---|
| fresh database | delete `db.sqlite3` (gitignored, one per worktree), then `poetry run python manage.py migrate` |
| server | `poetry run python manage.py runserver 127.0.0.1:8765 --noreload` in the background; wait for `/api/schema/` to answer |
| stop + clean | kill the server; delete `db.sqlite3` again |

## 2. Seed
Create exactly the rows the acceptance criteria need, through the ORM in the same database: `poetry run python manage.py shell -c "<python>"`, mirroring the fixtures in `<app>/tests/base.py`. Do not touch any other database.

## 3. Auth — reusable session
`poetry run python -m core.seed_evidence` creates (or reuses) the staff user `evidence` with an unusable password and prints one line of JSON: `{"username": …, "sessionid": …}`. It refuses to run when `DEBUG` is off. Send the `sessionid` as a cookie. Read-only requests need nothing more; unsafe methods also need the CSRF header (`X-CSRFToken` = the `csrftoken` cookie that `GET /admin/login/` sets). Swap this section when the API moves to token auth.

## 4. Capture
- API transcript (request line first, secrets redacted):
  `{ echo "GET /api/<path>"; curl -s -i -b "sessionid=$SESSION" http://127.0.0.1:8765/api/<path>; } | sed -E 's/(sessionid|csrftoken)=[^;[:space:]]+/\1=<redacted>/g' > ../docs/specs/evidence/<TICKET>/ac-<n>-api.txt`
  Also capture the call without the cookie when the criterion names the unauthenticated case.
- Screenshot (admin or any server-rendered page): write a Playwright storage state holding the cookie to a temp file outside the repo, then
  `npx --yes playwright@latest screenshot --channel msedge --viewport-size 1280,800 --load-storage <state.json> http://127.0.0.1:8765/admin/ ../docs/specs/evidence/<TICKET>/ac-<n>-ui.png`
  State file: `{"cookies":[{"name":"sessionid","value":"<SESSION>","domain":"127.0.0.1","path":"/","expires":-1,"httpOnly":true,"secure":false,"sameSite":"Lax"}],"origins":[]}`. `--channel chrome` works where Chrome is installed; otherwise `npx playwright install chromium` and drop `--channel`. No browser possible → record `not captured: <reason>`.
