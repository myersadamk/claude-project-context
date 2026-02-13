# MDX Authoring Rules

## Content Pattern

All MDX content uses a co-located `page.tsx` + `content.mdx` pattern:

```
src/app/<content-type>/<slug>/
├── page.tsx      # Layout wrapper, metadata, props
└── content.mdx   # Prose content
```

## Creating New Content — Required Steps

All steps are required. Content is not complete until it is both renderable and discoverable.

1. Create directory: `src/app/<content-type>/<slug>/`
2. Create `content.mdx` with prose content
3. Create `page.tsx` that imports `Content` from `./content.mdx`, wraps in the content type's layout component, and exports Next.js `metadata`
4. Register entry in the corresponding data file in `src/data/` with matching `href`

## page.tsx Structure

```tsx
import Content from "./content.mdx";
import { LayoutComponent } from "@/components/layout-component";

export const metadata = {
  title: "Post Title",
  description: "Post description for SEO",
};

export default function Page() {
  return (
    <LayoutComponent
      title="Post Title"
      description="Post description"
      date="YYYY-MM-DD"
      readTime="X min"
      badges={["Tag1", "Tag2"]}
      tags={["tag1", "tag2"]}
      showToc
    >
      <Content />
    </LayoutComponent>
  );
}
```

- Metadata lives in `page.tsx` — MUST NOT use MDX frontmatter (keeps type safety via TypeScript)
- Prose lives in `content.mdx` — MUST NOT put layout logic in MDX
- Props (title, date, tags) go to the layout component — MUST NOT hardcode in MDX

## MDX Component Registration

- Custom components are registered globally in `mdx-components.tsx` at the project root
- MDX authors MUST NOT import components manually in `.mdx` files — they are globally available
- New MDX components go in `src/components/mdx/`, then MUST be registered in `mdx-components.tsx`
- Every registered component MUST be documented in a local project rules file (e.g., an "Available MDX Components" table)

## Heading Rules

- `h2` and `h3` elements auto-generate anchor IDs via `slugify()` for table-of-contents support
- MUST use `##` and `###` in MDX for section headings — not `<h2>` tags
- MUST NOT skip heading levels (e.g., `##` then `####`)
