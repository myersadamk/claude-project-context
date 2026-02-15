# Testing Best Practices (Astro)

## Structure

- Unit tests: `tests/unit/**/*.test.ts` (Vitest)
- E2E tests: `tests/e2e/**/*.spec.ts` (Playwright)
- Test file mirrors source: `src/utils/navigation.ts` -> `tests/unit/navigation.test.ts`

## What to Test

### Unit (Vitest)

- Utility functions (`src/utils/`)
- Content collection schema validation
- Data transformations, filters, sorting logic
- Pure functions with clear inputs/outputs

### E2E (Playwright)

- Page loads and renders correct content
- Navigation between pages works
- Interactive components (search, mobile menu)
- 404 page displays for unknown routes
- Critical user journeys end-to-end

### Don't Test

- Astro's own rendering (framework's job)
- Tailwind class application (visual, not logical)
- Third-party library internals

## Conventions

- Test behavior, not implementation
- One assertion concept per test (multiple `expect` calls are fine if testing one behavior)
- Descriptive test names: `it('filters draft pages from navigation')`
- MUST NOT add test-specific logic to source code
- Tests run in pre-commit hook — keep them fast

## Commands

- `npm run test` — unit tests
- `npm run test:e2e` — e2e tests (requires build)
