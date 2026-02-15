# Code Review Checklist

## Quality Gate

Before reviewing, load all files in `.claude/rules/`.

## Verification Commands

Run the verification commands from your stack's review rule (e.g., `python-cli-review.md`, `typescript-web-review.md`). All MUST pass before approval.

## Checklist

### Correctness

- [ ] Code does what it's supposed to do
- [ ] Logic handles edge cases and error states
- [ ] No dead code or unused imports
- [ ] No debug logging left in production code

### Security (-> universal-security.md)

- [ ] No secrets in source
- [ ] User input sanitized at system boundaries
- [ ] Security headers maintained

### Code Structure (-> universal-code-structure.md)

- [ ] Functions under 100 lines, aim for ~50
- [ ] Maximum 3 levels of nesting
- [ ] Early returns for preconditions
- [ ] Consistent abstraction level within each function

### Testing

- [ ] New logic has tests
- [ ] All tests pass
- [ ] Tests verify behavior, not implementation details

### Stack-Specific

- [ ] Review against the active stack review rule (`*-review.md`)

## Exceptions

If a rule needs to be broken:

1. Document the reason in the PR description
2. Add a code comment explaining the exception
3. Consider if the rule should be updated instead

MUST NOT make silent exceptions. MUST NOT merge rule violations without discussion.
