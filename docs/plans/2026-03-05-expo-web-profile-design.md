# Expo Web Profile Design

## Overview

New `expo-web` profile for Expo SDK 52+ projects (web-first, mobile later). Includes changes to the shared `typescript-web` layer and a new framework-specific rule set.

## Profile Config

```yaml
expo-web:
  rules:
    - universal-coding
    - typescript-web
    - expo-web
  skills:
    - vibesec
    - cpc-init
    - cpc-audit
    - cpc-extract
```

## Changes to `typescript-web` (shared layer)

### `typescript-web-best-practices.md` — Add Section

New "Architecture Boundaries" section after "File Size":
- Pure-logic modules must not import from React/RN/UI frameworks
- Hooks bridge logic to components — components must not import directly from pure-logic layer
- No UI primitives (refs, event objects, JSX) passed into pure-logic modules
- Platform-specific behavior injected via function arguments, not framework imports

### `typescript-web-styling.md` — New File (~35 lines)

General styling principles extracted from `typescript-web-tailwind.md`:
- Semantic color tokens (CSS custom properties or theme variables)
- Spacing from defined scale
- Shadow hierarchy from design system
- Motion tokens, respect `prefers-reduced-motion`
- Mobile-first responsive approach
- Points to framework-specific file for implementation syntax

### `typescript-web-state.md` — New File (~45 lines)

Zustand-leaning state management principles:
- One store per domain, actions inside store, no external mutation
- Flat state shape, derive with selectors
- Local vs global vs URL state guidance
- Persistence via `persist` middleware, abstract storage backend
- Selector discipline to prevent re-renders

### `typescript-web-tailwind.md` — Shrink

Move general principles (colors, spacing, shadows, motion) to `styling.md`. Keep Tailwind-syntax-specific rules: utility-first model, class ordering, responsive syntax, `@apply` policy, component extraction, anti-patterns.

## New `expo-web` Rule Set (4 files)

### `expo-web-review.md` (~40 lines)

Verification commands: `npx expo lint`, `npx tsc --noEmit`, `npx jest`, `npx expo export --platform web`. Checklist covering correctness, styling, state, security, types with cross-references to other rule files.

### `expo-web-framework.md` (~60 lines)

- Expo Router file-based routing conventions, typed routes
- Layout patterns (root, tabs, nesting limit of 2)
- Modal routes via `(modal)/` group
- Route parameter typing and validation
- Auth guards via layout redirects
- Platform-specific code: `Platform.select()`, file extensions (`.web.tsx`, `.native.tsx`)
- Component conventions: functional only, SafeAreaView, Pressable, accessibility

### `expo-web-nativewind.md` (~40 lines)

- Nativewind v4+ setup with Expo SDK 52+
- `className` prop usage, `styled()` for third-party components
- Platform divergences: shadows, hover, CSS Grid, gradients
- Responsive behavior differences between web and native
- Anti-patterns: no `@apply`, no web-only CSS features in shared components

### `expo-web-zustand.md` (~45 lines)

- Store structure: one per domain, colocated in `src/stores/`
- Persistence: `persist` middleware with platform-appropriate storage backend
- Hydration handling, store versioning and migration
- Selector discipline with `useShallow`
- State machines for multi-step flows (explicit status unions, no boolean flags)
- Middleware ordering: `persist(immer(store))`

## Impact on Existing Profiles

Next.js and Astro automatically gain `typescript-web-styling.md` and `typescript-web-state.md`. The tailwind file shrinks but no rules are removed — they move up a layer. Net positive for all `typescript-web` consumers.
