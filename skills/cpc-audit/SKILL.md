---
name: cpc:audit
description: Reload installed rules into context and audit recent changes against them. Use when rules may have drifted out of context during a long session, or before a PR.
---

# cpc:audit

## When to Use

- Before creating a PR or commit
- When you've been working for a while and rules may have scrolled out of context
- When the user asks to check their work against the rules

## Steps

1. **Reload rules:** Read every `.md` file in `.claude/rules/` in the current project. This forces the rules back into your active context.

2. **Identify changes:** Run `git diff --cached` and `git diff` to see staged and unstaged changes. If both are empty, check `git diff HEAD~1` for the most recent commit.

3. **Audit against each rule:** For each rule file you loaded, check the identified changes against it. Focus on:
   - Violations: things the diff does that the rule prohibits
   - Missing practices: things the rule requires that the diff doesn't follow
   - Skip rules that aren't relevant to the changed files (e.g., skip TypeScript rules for Python changes)

4. **Report findings:** Present a checklist grouped by rule file:
   - ✅ Compliant items (brief)
   - ❌ Violations with specific file:line references and what to fix

5. **Verification reminder:** If any `*-review.md` file defines verification commands, remind the user to run them. Quote the exact commands.

## Scoping

- Audit the **current diff only**, not the entire codebase
- Skip rule files that don't apply to the changed file types
- Keep findings actionable — specific file and line references, not general advice
