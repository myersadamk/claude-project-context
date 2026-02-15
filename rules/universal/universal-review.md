# Code Review Checklist

## Quality Gate

Before reviewing:
1. Load all files in `.claude/rules/`
2. Identify the stack-specific `*-review.md` file (e.g., `typescript-web-review.md`, `python-cli-review.md`)
3. Run the verification commands defined in that file

## Checklist

### Correctness

- [ ] Code does what it's supposed to do
- [ ] Logic handles edge cases and error states
- [ ] No dead code or unused imports
- [ ] No debugging artifacts left in production code

### Security (-> universal-security.md)

- [ ] No secrets in source
- [ ] User input sanitized at system boundaries
- [ ] Security headers maintained

### Code Structure (-> universal-code-structure.md)

- [ ] Functions under 50 lines (hard ceiling: 100)
- [ ] Maximum 3 levels of nesting
- [ ] Early returns for preconditions
- [ ] Consistent abstraction level within each function
- [ ] No duplicated blocks with minor variations

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
