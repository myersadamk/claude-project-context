# Expo Zustand Patterns

## Store Structure

- One store per domain: `useDrillStore`, `useProgressStore`, `useSettingsStore`
- Colocate store files in `src/stores/`
- Each store file exports a single `use*Store` hook — no bare store exports
- MUST NOT access store state outside React components without `use*Store.getState()`

## Persistence

- Use `persist` middleware for state that survives app restarts
- Storage backend:
  - Web: `localStorage` (default, no config needed)
  - Native: `AsyncStorage` via a custom storage adapter
- MUST define a `name` key for each persisted store (used as storage key)
- MUST define a `partialize` function — persist only what's needed, not derived state
- MUST handle hydration: use `onRehydrateStorage` or check `hasHydrated` before rendering dependent UI
- Version persisted stores with `version` + `migrate` when shape changes

## Selectors

- MUST use selectors to subscribe to specific slices:
  `const score = useDrillStore(s => s.score)` — not `const { score } = useDrillStore()`
- For multiple values, use `useShallow` from `zustand/react/shallow` to prevent unnecessary re-renders
- Derived values: compute in selectors, not in store state

## State Machines

- Model multi-step flows as explicit states in the store:
  `status: 'idle' | 'configuring' | 'active' | 'grading' | 'complete'`
- Transition actions MUST validate current state before transitioning
- MUST NOT use boolean flags for mutually exclusive states (`isActive && isGrading` should be impossible)

## Middleware

- `persist` for storage (see above)
- `immer` only if state updates are deeply nested — prefer flat state shape instead
- If combining: `persist(immer(store))` — persist wraps immer
- `devtools` middleware in development only
