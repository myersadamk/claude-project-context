# Code Review Checklist

## Quality Gate

Before reviewing, load all files in `.claude/rules/`.

## Verification Commands

All MUST pass before approval:

```bash
npm run lint && npm run typecheck && npm run format:check && npm run test && npm run build
```

Skip `build` only for documentation-only changes. All others MUST pass.

## Checklist

### Correctness

- [ ] Code does what it's supposed to do
- [ ] Logic handles edge cases and error states
- [ ] No dead code or unused imports
- [ ] No `console.log` left in production code

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

### Security (-> universal-security.md)

- [ ] No secrets in source
- [ ] User input sanitized at system boundaries
- [ ] CSP headers maintained

### Design System (-> local design-system.md)

- [ ] Colors use semantic tokens defined in design-system
- [ ] Spacing follows defined scale
- [ ] Typography matches defined families and scale
- [ ] Motion uses design-system duration and easing tokens
- [ ] Skip if design-system.md is not yet populated

### Testing

- [ ] New logic has unit tests
- [ ] New pages/interactions have e2e tests
- [ ] All tests pass

### Framework-Specific

- [ ] Review against the active framework rules (astro-framework.md, nextjs-architecture.md, etc.)

## Exceptions

If a rule needs to be broken:

1. Document the reason in the PR description
2. Add a code comment explaining the exception
3. Consider if the rule should be updated instead

MUST NOT make silent exceptions. MUST NOT merge rule violations without discussion.
