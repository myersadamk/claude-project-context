# State Management

## Store Design (Zustand)

- One store per domain (`useDrillStore`, `useProgressStore`, `useSettingsStore`)
- Actions MUST be defined inside the store via `set` — no external mutation
- MUST NOT export the bare store — export only the `use*Store` hook
- MUST NOT access store state outside React components without `use*Store.getState()`

## State Shape

- Prefer flat state over deeply nested objects
- Derived values MUST be computed in selectors, not stored
- Model multi-step flows as explicit status unions: `'idle' | 'loading' | 'active' | 'error'`
- MUST NOT use boolean flags for mutually exclusive states — use a status union instead

## Selectors

- MUST use selectors to subscribe to specific slices:
  `const score = useGameStore(s => s.score)` — not `const { score } = useGameStore()`
- For multiple values, use `useShallow` from `zustand/react/shallow` to prevent unnecessary re-renders

## When to Use What

- **Local component state** (`useState`): ephemeral UI state — form inputs, open/close toggles, hover
- **URL state** (search params, route params): anything that should be shareable or bookmarkable
- **Global store** (Zustand): state that multiple unrelated components need — user session, app-wide settings, domain data
- MUST NOT put ephemeral UI state in the global store
- MUST NOT use React Context for state that changes frequently — it re-renders all consumers

## Persistence

- Use Zustand's `persist` middleware for state that survives app restarts
- MUST define a `name` key for each persisted store (used as the storage key)
- MUST use `partialize` to persist only what's needed — never persist derived state
- Version persisted stores with `version` + `migrate` when the shape changes
- Abstract the storage backend (localStorage for web, AsyncStorage for native) so stores are portable

## Middleware

- `persist` for storage (see above)
- `immer` only if state updates are deeply nested — prefer flat state shape instead
- If combining: `persist(immer(store))` — persist wraps immer
- `devtools` in development only
- If using a different state library, adapt these principles accordingly
