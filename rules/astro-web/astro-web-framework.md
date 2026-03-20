# Astro Best Practices

## Component Model

- `.astro` components are the default — only use framework components (React, etc.) when client-side interactivity is required
- Keep components pure: props in, HTML out. Side effects belong in page-level scripts
- Layouts wrap pages. Components compose within pages. MUST NOT nest layouts
- Architecture follows Astro's natural model: content collections are the data layer, `.astro` files are the view, `src/utils/` holds logic

## Images

- MUST use Astro's `<Image>` / `<Picture>` from `astro:assets`, never raw `<img>`
- Local images MUST go in `src/` (not `public/`) so Astro can optimize them
- `public/` is only for images that MUST NOT be processed (favicons, OG images)
- MUST provide `alt`, `width`, and `height` attributes on all images

## Content Collections

- All structured content MUST use content collections with Zod schemas
- Schemas MUST be defined in `src/content.config.ts`, never rely on unvalidated frontmatter
- Query with `getCollection()` / `getEntry()`, not raw file reads
- Filter drafts at query time: `filter: (entry) => !entry.data.isDraft`

## Client-Side JavaScript

- Astro is zero-JS by default. Every `<script>` tag or client directive is a deliberate choice
- Prefer `<script>` tags in `.astro` files over framework hydration
- When hydration is needed: `client:load` for above-fold interactive, `client:visible` for below-fold
- MUST NOT use `client:only` unless the component genuinely cannot SSR

## Page Transitions

- MUST include `<ClientRouter />` from `astro:transitions` in the base layout's `<head>`
- Without it, every navigation is a full page load causing FOUC, layout shift, and erratic tab titles
- `ViewTransitions` was renamed to `ClientRouter` in Astro 5 — MUST use the new name
- If a page needs to opt out, use `<a data-astro-reload>` on the specific link

## Routing & Pages

- File-based routing in `src/pages/`. One page = one route
- Dynamic routes use `[...slug].astro` with `getStaticPaths()`
- Kebab-case for all filenames
- Every page MUST have `<title>` and meta description (via layout props)

## Security (Astro-Specific)

- Static site = small attack surface. Keep it that way
- MUST NOT use `set:html` with user-supplied content
- Client-side `<script>` tags MUST NOT fetch or eval external code
- If adding SSR or API routes, invoke the `vibesec` skill for a full security review
- Security headers maintained in `public/_headers`:
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY
  - Referrer-Policy: strict-origin-when-cross-origin
  - Permissions-Policy: restrictive
  - CSP: changes require justification
