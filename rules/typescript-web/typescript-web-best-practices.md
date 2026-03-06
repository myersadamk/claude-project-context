# Best Practices

## DRY / Extraction

- MUST extract repeated markup into a component after 2 occurrences
- MUST move shared utilities to a shared location after use in 2+ files
- MUST move shared constants to a data or constants file after use in 2+ files
- MUST co-locate first — only extract to shared locations when reuse is proven
- MUST NOT create premature abstractions for single-use patterns
- MUST NOT create `utils/`, `helpers/`, or `common/` grab-bag files

## Naming

- Components: `PascalCase` — file name MUST match the default export (`ProjectCard.tsx` -> `export function ProjectCard`)
- Utilities: `camelCase`
- Data files: `kebab-case`
- Boolean props and variables: MUST prefix with `is`, `has`, `should`, or `show`
- Event handler props: MUST prefix with `on` (`onClick`, `onSubmit`)
- Event handler functions: MUST prefix with `handle` (`handleClick`, `handleSubmit`)

## Imports

- MUST use the project's path alias (e.g., `@/`) for all non-relative imports
- MUST NOT use relative imports that climb more than one level (`../../` is banned)
- MUST group imports with a blank line between groups:
  1. Framework imports (React, Next.js, Astro, etc.)
  2. External packages
  3. Internal imports (via path alias)
  4. Relative imports (same directory only)

## Error Handling

- MUST only validate at system boundaries (user input, external APIs)
- MUST NOT add defensive try/catch around code that cannot throw
- MUST NOT add fallback values for props that are always provided
- MUST NOT add null checks for values that are guaranteed by TypeScript types

## File Size

- MUST investigate extraction opportunities if a component file exceeds 200 lines
- This is a smell threshold, not a hard limit — but it MUST trigger a review of whether the component is doing too much

## Architecture Boundaries

- If the project has a pure-logic layer (e.g. `src/engine/`, `src/lib/core/`, `src/domain/`), those modules MUST NOT import from React, React Native, or any UI framework
- Pure-logic modules MUST be testable with zero UI dependencies
- Hooks are the bridge between logic and components — components MUST NOT import directly from the pure-logic layer; they consume it through hooks
- MUST NOT pass UI primitives (refs, event objects, JSX) into pure-logic modules
- If a module needs platform-specific behavior, inject it via function arguments or configuration, not framework imports

## Scripts

- `package.json` MUST expose these standard script names:
  - `dev` — start the development server
  - `build` — production build or export
  - `lint` — run the linter
  - `test` — run the test suite
  - `typecheck` — run `tsc --noEmit`
- Framework-specific commands MUST be aliased to these standard names so `npm run dev`, `npm run build`, etc. work consistently across all projects
- Additional framework-specific scripts (e.g. `dev:web`, `start:android`) are fine alongside the standard names

## Dependencies

- MUST NOT add new dependencies without explicit discussion
- MUST prefer existing dependencies over new ones
- MUST NOT add polyfills or compatibility libraries for features supported by the target runtime
