# {{area_name}} stack

<!-- When: any work in {{area}}/ — SDK, scripts, layout, navigation, lint setup, how the app talks to the API. cwd = {{area}}/. -->

## Stack
- Expo SDK, React, React Native and TypeScript versions: read `{{area}}/package.json` (the `expo` major selects the docs: `https://docs.expo.dev/versions/v<major>.0.0/`).
- TypeScript strict (`tsconfig.json` extends `expo/tsconfig.base`). `{{area}}/.claude/settings.json` enables the Expo plugin for Claude Code.

## Layout (blank-typescript template)
```
index.ts     registers the root component
App.tsx      root component (no router yet)
app.json     Expo config (name, slug, icons, plugins)
assets/      icons, splash
```
Navigation: none yet. Expo's guidance (`{{area}}/docs/ai/expo-official.md`) prefers Expo Router with routes under `src/app/` once the app has more than one screen; adopting it is a ticket-level decision.

## Commands
| command | does |
|---|---|
| `npm install` | install deps (fresh clone / worktree) |
| `npx expo start` | dev server (`a` Android, `i` iOS, `w` web) |
| `npx expo install <pkg>` | add a dependency at its SDK-compatible version |
| `npx tsc --noEmit` | type check (gate) |
| `npm run lint` | ESLint via `expo lint` (gate) |
| `npx expo export --platform android --output-dir <tmp dir>` | bundles the JS for Android without a device (gate) |
| `npx expo-doctor` | diagnose dependency / config problems |

## Lint — first-time setup
A fresh template has no ESLint. If `{{area}}/eslint.config.js` is missing: run `npx expo lint` — it installs `eslint` + `eslint-config-expo`, writes `eslint.config.js`, adds the `lint` script, and **exits 1**. Run it again (exit 0) and commit `eslint.config.js`, `package.json`, and the lock file.

## API integration
- Base URL: none yet — add `EXPO_PUBLIC_API_URL` and read it in one module when the first endpoint is used.
- Endpoints used: none yet — list each endpoint the app calls here, with ✓ / ✗ for whether the API serves it. A native app can't use Django session cookies the way a browser does, so the API needs a token-style auth class before the first authenticated call.
