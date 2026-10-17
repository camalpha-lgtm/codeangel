# {{area_name}} evidence

<!-- When: gathering proof that a change works (build-loop VERIFY, check V9) or showing a screen by hand. cwd = {{area}}/; POSIX shell (Git Bash on Windows). -->

Recipe: start → seed → auth → capture. Artefacts go to `docs/specs/evidence/<TICKET>/` at the repo root (`../docs/specs/evidence/<TICKET>/` from `{{area}}/`); name them `ac-<n>-ui.png` / `ac-<n>-cli.txt`. Never commit credentials.

## Prerequisite — a web target
A native-only Expo app cannot be screenshotted headlessly. The web target needs `react-native-web` and `react-dom` (`npx expo install react-native-web react-dom`); until a ticket adds them, UI proof is `not captured: no web target (react-native-web / react-dom not installed)`. A device or emulator screenshot is an alternative when the harness can reach one.

## 1. Start
`npx expo start --web --port 8081` in the background; wait until `http://localhost:8081` answers. Stop it afterwards.

## 2. Seed
The app holds no data of its own: seed the API area it talks to (see that area's `docs/ai/evidence.md`) and point the app at it with `EXPO_PUBLIC_API_URL` for this run only.

## 3. Auth
Use the API area's evidence session. Anything the app needs at runtime (token, cookie) is injected for the run through the environment or a storage state file kept outside the repo, never written into app code.

## 4. Capture
`npx --yes playwright@latest screenshot --channel msedge --viewport-size 390,844 http://localhost:8081 ../docs/specs/evidence/<TICKET>/ac-<n>-ui.png` (add `--load-storage <state.json>` for an authenticated screen; `--channel chrome` where Chrome is installed, else `npx playwright install chromium` and drop `--channel`). For a flow rather than a first screen, drive it with the browser tool your harness provides and screenshot the state the criterion names. No browser possible → `not captured: <reason>`.
