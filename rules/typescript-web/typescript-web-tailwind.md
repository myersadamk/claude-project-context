# Tailwind CSS Rules

## General

- All styling through Tailwind utility classes — MUST NOT use inline `style` attributes
- MUST NOT use `!important`
- MUST NOT use arbitrary values (`w-[347px]`) without a documented reason in a code comment
- Custom CSS only in the project's global stylesheet for design tokens and prose

## Class Ordering

Follow logical grouping: layout -> sizing -> spacing -> typography -> visual -> interactive

```
flex items-center gap-4 w-full p-4 text-sm font-medium bg-surface border border-border rounded-xl hover:bg-surface/80
```

## Responsive

- Mobile-first: bare utilities are mobile, breakpoints layer up
- Standard breakpoints: `sm:` `md:` `lg:`
- MUST NOT use `xl:` or `2xl:` unless justified with a code comment

## Colors

- All colors from CSS custom properties (semantic tokens)
- MUST NOT hard-code hex/rgb/hsl values in class names
- Use opacity modifiers on token colors: `bg-primary/80`, `text-muted-foreground/60`

## Spacing

- MUST follow the project's defined spacing scale (see local `design-system.md`)
- If design-system.md is not yet populated, use Tailwind's default scale consistently
- Prefer consistent gaps (`gap-4`, `gap-8`) over mixed margin/padding
- MUST NOT use off-scale values without a code comment explaining why

## Shadows

- MUST follow shadow levels defined in the project's `design-system.md`
- Prefer borders over shadows for visual separation

## Animation

- Duration and easing MUST use design-system motion tokens
- See local `design-system.md` for project-specific values

## Component Extraction vs. Semantic Classes

- Repeated utility patterns MUST be extracted into components, not CSS classes
- `@apply` is permitted ONLY in the project's global stylesheet for:
  - Prose/markdown content styling that can't be componentized
  - Base element styles (e.g., anchor tags inside rendered markdown)
- MUST NOT use `@apply` inside component files

## Anti-Patterns

- MUST NOT use `@apply` in components — defeats the utility-class model
- MUST NOT use Tailwind in `<style>` blocks — keep styles in template markup
- MUST NOT concatenate class strings for variants — use the project's class merging utility
