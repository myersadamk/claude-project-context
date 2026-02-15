# Next.js Architecture Rules

## Server vs. Client Components

- MUST use Server Components by default
- MUST only add `"use client"` when the component uses `useState`, `useEffect`, `useRef`, event handlers, or browser APIs
- MUST NOT add `"use client"` for components that only receive and render props

## State Escalation Ladder

Use the lowest rung that solves the problem:

1. **Data imports** — Static data from `src/data/` as typed arrays. Covers content that doesn't change per-interaction.
2. **`useState` / `useReducer`** — Local UI state (toggles, form inputs, filter selections). Stays in the owning component.
3. **URL searchParams** — Shareable, bookmarkable state (filters, pagination). Use Next.js App Router conventions.
4. **React Context** — Cross-cutting concerns that span the component tree (theme, auth session).
5. **Stop and brainstorm** — If you think you need a state management library (Redux, Zustand, Jotai), open a brainstorming session first.

MUST NOT add a state management library without explicit discussion.

## Data Layer

- Data lives in `src/data/` as typed TypeScript arrays and interfaces
- MUST NOT create API routes, service layers, or database connections unless explicitly requested
- If a page needs data, import it directly from `src/data/`

## Component Organization

| Directory | Purpose | Rules |
| --- | --- | --- |
| `src/components/ui/` | shadcn/ui primitives | MUST NOT modify directly — override via composition |
| `src/components/` | Project components | Single file per component unless it has subcomponents |
| `src/components/mdx/` | MDX-specific components | MUST register in `mdx-components.tsx` |

- Route-specific components that aren't reusable MUST stay in the route directory, not in `src/components/`
- MUST NOT create `components/common/`, `components/shared/`, or similar grab-bag directories

## shadcn/ui

- MUST use shadcn/ui primitives before building custom (Button, Card, Badge, etc.)
- MUST compose primitives rather than building from scratch
- MUST NOT modify shadcn/ui source files — override behavior via composition and wrapper components
- Use `cn()` from `@/lib/utils` for conditional class merging

## Routing

- Every route is a directory in `src/app/` with a `page.tsx`
- MUST use Next.js file-system routing conventions — no custom route handlers unless explicitly needed

## Utilities

- Shared utilities live in `src/lib/`
- `cn()` from `@/lib/utils` for conditional class merging
- `slugify()` from `@/lib/slugify` for URL-safe strings
- MUST NOT create utility grab-bags — each utility file has a focused purpose
