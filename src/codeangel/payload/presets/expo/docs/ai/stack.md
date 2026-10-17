# {{area_name}} stack

<!-- When: any work in {{area}}/ — SDK, scripts, layout, navigation, how the app talks to the API. cwd = {{area}}/. -->

## Stack
- Expo SDK: see `expo` in `{{area}}/package.json` (docs: https://docs.expo.dev/versions/<sdk>/). React Native + React versions are pinned by the SDK.
- TypeScript strict (`tsconfig.json` extends `expo/tsconfig.base`).

## Scripts (`{{area}}/package.json`)
| command | does |
|---|---|
| `npm install` | install deps (fresh clone / worktree) |
| `npx expo start` | dev server (press `a` Android, `i` iOS, `w` web) |
| `npx tsc --noEmit` | type check (gate) |
| `npx expo lint` | lint (gate) |

## Layout
```
App.tsx      root component (blank template; add expo-router when navigation is needed)
index.ts     registers the root component
app.json     Expo config (name, slug, icons, plugins)
assets/      icons, splash
```

## API integration
- Base URL: none yet — add `EXPO_PUBLIC_API_URL` and read it in one module when the first endpoint is used.
- Endpoints used: none yet — list each endpoint the app calls here, with ✓ / ✗ for whether the API serves it.
