# {{area}}/AGENTS.md — Expo app

<!-- Loaded for any work under {{area}}/. Budget ≤ 50 lines. Detail → {{area}}/docs/ai/, gotchas → {{area}}/docs/learnings/. -->

React Native via Expo · TypeScript (strict). Run every command from `{{area}}/`.

## Expo changes fast
Before writing Expo code, read the docs for the SDK in `{{area}}/package.json` (`expo` dependency, e.g. `~54.0.0` → https://docs.expo.dev/versions/v54.0.0/). Never rely on memory of an older SDK.

## Router
| when | read |
|---|---|
| stack, scripts, layout, navigation, how the app talks to the API | `{{area}}/docs/ai/stack.md` |
| the app needs a new / changed endpoint | the API area's `AGENTS.md` first (API before client) |
| {{area_name}} gotchas | `{{area}}/docs/learnings/README.md` |

## Always
- Add native / Expo packages with `npx expo install <pkg>` (SDK-compatible versions), not `npm install`.
- API base URL lives in one config spot (`EXPO_PUBLIC_*` env / app config) — never hardcoded hosts or LAN IPs.
- Everything in the bundle is public: no secrets in the app.
- TypeScript strict; no `any` without a comment saying why.

## Done — gates, relative to the base commit
1. Types: `npx tsc --noEmit` exit 0.
2. Lint: `npx expo lint` clean on changed files (first run installs ESLint config — commit it).
3. Tests: once a test runner exists, its command in `{{area}}/docs/ai/stack.md` passes.
4. Bundles: `npx expo export --platform web --output-dir <tmp>` (or a device run) succeeds when the change touches app code or config.
