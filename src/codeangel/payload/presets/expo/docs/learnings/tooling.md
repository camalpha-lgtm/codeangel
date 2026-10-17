# {{area_name}} tooling

<!-- When: expo lint, expo export, expo-doctor, or create-expo-app template trouble in {{area}}/. -->

- **The first `npx expo lint` on a fresh blank-typescript app installs ESLint, writes `eslint.config.js`, adds a `lint` script — and exits 1; the second run exits 0.** — a CI step or gate that runs lint before this bootstrap fails. Bootstrap once locally and commit the result. src: codeangel seed, verified on a generated app (Expo SDK 58)
- **`npx expo export --platform android --output-dir <dir>` bundles the JS with no emulator or native toolchain; `--platform web` fails on the blank template.** — web support isn't set up there (the error says to install the web dependencies or remove `web` from the platforms). Use the Android export as the "app bundles" gate. src: codeangel seed, verified
- **create-expo-app writes its own `AGENTS.md` (and `.claude/settings.json`).** — `codeangel add expo` moves that file to `{{area}}/docs/ai/expo-official.md` and routes to it instead of overwriting it. src: codeangel seed, verified
- **`npx create-expo-app` refuses a non-empty target directory and asks whether to `git init` when run inside a repo.** — create the app before `codeangel add expo`; answer the prompt with the default (skip) so the area isn't a nested repo. src: codeangel seed, verified
