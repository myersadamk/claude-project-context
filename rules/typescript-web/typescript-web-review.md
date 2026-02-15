# TypeScript Web — Review Checklist

## Verification Commands

All MUST pass before approval:

```bash
npm run lint && npm run typecheck && npm run format:check && npm run test && npm run build
```

Skip `build` only for documentation-only changes. All others MUST pass.

## Checklist

### TypeScript (-> typescript-web-types.md)

- [ ] No `any`, `as`, `!`, or `@ts-ignore`
- [ ] Explicit return types on all functions
- [ ] Proper type narrowing over casting
- [ ] Props are properly typed

### Accessibility (-> typescript-web-ui.md)

- [ ] Semantic HTML, correct heading hierarchy
- [ ] Keyboard navigable, visible focus states
- [ ] ARIA labels on icon-only buttons
- [ ] WCAG AA contrast minimum

### Tailwind (-> typescript-web-tailwind.md)

- [ ] No `!important`, no unjustified arbitrary values
- [ ] No hard-coded colors — semantic tokens only
- [ ] Mobile-first responsive approach
- [ ] Repeated patterns extracted to components, not CSS classes

### Design System (-> local design-system.md)

- [ ] Colors use semantic tokens defined in design-system
- [ ] Spacing follows defined scale
- [ ] Typography matches defined families and scale
- [ ] Motion uses design-system duration and easing tokens
- [ ] Skip if design-system.md is not yet populated

### Framework-Specific

- [ ] Review against the active framework rules (astro-web-framework.md, nextjs-web-architecture.md, etc.)
