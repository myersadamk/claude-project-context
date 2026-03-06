# Expo Framework Rules

## Expo Router Conventions

- MUST use file-based routing in `app/` directory
- Layouts MUST be in `_layout.tsx` — shared UI (headers, tab bars, providers) lives here
- Screen-specific logic MUST stay in route files, not leak into layouts
- Route groups use parentheses: `(tabs)/`, `(auth)/`, `(modal)/`
- MUST use typed routes — enable `experiments.typedRoutes` in app config
- MUST use `<Link>` or `router.push()` for navigation, never raw `<a>` tags

## Layout Patterns

- Root `_layout.tsx`: providers (theme, auth, stores), global error boundary
- `(tabs)/_layout.tsx`: tab navigator configuration
- Nested layouts: use sparingly, only when a group of routes shares persistent UI
- MUST NOT nest more than 2 layout levels deep without documented justification

## Modal Routes

- Modal screens live in a `(modal)/` route group
- Present modals via `router.push('/(modal)/screen-name')`
- Modal layout uses `presentation: 'modal'` in screen options
- MUST handle dismiss with `router.back()`, not `router.replace()`

## Route Parameters

- MUST type all route params using Expo Router's typed routes
- Dynamic routes: `[id].tsx` for required params, `[...rest].tsx` for catch-all
- MUST validate params at the route level before passing to hooks/components
- MUST NOT pass raw param strings deep into the component tree — parse at the top

## Auth Guards

- Auth state checked in root layout via redirect
- `useRootNavigationState()` to wait for navigator readiness
- Unauthenticated users redirect to `/(auth)/login`
- MUST NOT conditionally render route content based on auth — redirect instead

## Platform-Specific Code

- Use `Platform.select()` for small inline differences
- Use file extensions (`.web.tsx`, `.native.tsx`, `.ios.tsx`) for divergent implementations
- MUST NOT use `Platform.OS === 'web'` checks inside render logic — extract to a hook or use file extensions
- Web-only APIs (DOM, `window`, `document`) MUST be isolated in `.web.tsx` files
- Native-only modules MUST be isolated in `.native.tsx` files

## Scripts

- `package.json` MUST define these standard aliases (see typescript-web-best-practices.md):
  - `"dev": "expo start"`
  - `"dev:web": "expo start --web"`
  - `"build": "expo export --platform web"`
  - `"lint": "expo lint"`
  - `"test": "jest"`
  - `"typecheck": "tsc --noEmit"`
- The Expo template defaults (`start`, `web`, `ios`, `android`) MAY remain alongside the standard names

## Component Conventions

- Functional components + hooks only — no class components
- MUST use `SafeAreaView` or `useSafeAreaInsets()` for screens with native targets
- Pressable over TouchableOpacity — `Pressable` is the modern API
- MUST set `accessible` and `accessibilityLabel` on all interactive elements
- Touch targets MUST be at least 44x44pt
