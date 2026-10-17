# {{area}}/AGENTS.md — Expo app

<!-- Loaded for any work under {{area}}/. Budget ≤ 50 lines. Detail → {{area}}/docs/ai/, gotchas → {{area}}/docs/learnings/. -->

React Native via Expo · TypeScript (strict) · ESLint (`eslint-config-expo`). Run every command from `{{area}}/`.

## Expo changes fast — do not trust memory
Before writing Expo / EAS / React Native code: read the major version of `expo` in `{{area}}/package.json`, then the matching docs (`https://docs.expo.dev/versions/v<major>.0.0/`). Index with corrections to common LLM mistakes: https://docs.expo.dev/llms.txt.

## Router
| when | read |
|---|---|
| stack, scripts, layout, navigation, how the app talks to the API | `{{area}}/docs/ai/stack.md` |
| writing / changing Expo code, adding packages, routing, EAS builds | `{{area}}/docs/ai/expo-official.md` (Expo's own agent guidance) |
| the app needs a new / changed endpoint | the API area's `AGENTS.md` first (API before client) |
| gathering proof a change works: web target, screenshot | `{{area}}/docs/ai/evidence.md` |
| {{area_name}} gotchas | `{{area}}/docs/learnings/README.md` |

## Always
- Add packages with `npx expo install <pkg>` (SDK-compatible versions), never `npm install <pkg>`.
- `ios/` and `android/` are generated (Continuous Native Generation): never hand-edit; configure in `app.json` and config plugins.
- API base URL lives in one config spot (`EXPO_PUBLIC_*` env / app config) — never hardcoded hosts or LAN IPs. Everything in the bundle is public: no secrets in the app.
- TypeScript strict; no `any` without a comment saying why.

## Done — gates, relative to the base commit
1. Types: `npx tsc --noEmit` exit 0.
2. Lint: `npm run lint` exit 0 (first-time setup: `{{area}}/docs/ai/stack.md`).
3. Bundles: `npx expo export --platform android --output-dir <tmp dir>` exit 0 when the change touches app code, config, or dependencies.
4. Dependencies or config changed: `npx expo-doctor` reports no issues.
5. Tests: once a test runner exists, its command is in `{{area}}/docs/ai/stack.md` and passes.
