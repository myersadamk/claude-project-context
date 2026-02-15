---
name: cpc-audit
description: Use when you want to check recent code changes against installed cpc rules. Reloads rules into context and audits the current diff.
user-invocable: true
disable-model-invocation: true
---

# cpc-audit

Reload installed rules into context and audit recent changes against them.

## Why This Exists

Rules loaded at conversation start drift out of context during long sessions. There's no way to "refresh" awareness of them — and no structured check that recent changes actually comply. This skill solves both problems in one pass.

## Process

### 1. Reload Rules

Read **every** `.md` file in `.claude/rules/`. This forces the full rule set back into context.

Skip non-rule files (e.g. dotfiles).

List what was loaded:
```
Loaded 6 rules:
  universal-coding-code-structure.md
  universal-coding-review.md
  universal-coding-security.md
  python-cli-best-practices.md
  python-cli-click.md
  python-cli-review.md
```

### 2. Identify Changes

Run:
```bash
git diff --cached
git diff
```

If both are empty, check `git diff HEAD~1` for the most recent commit.

If all are empty, report "No changes to audit" and stop.

If there are staged and unstaged changes, audit both — note which is which.

### 3. Audit Against Rules

Walk through each loaded rule file. For each rule that is relevant to the changed files, check compliance.

**Be specific.** Don't check TypeScript rules against Python files. Don't check Tailwind rules if no CSS/markup changed. Match rules to the files that changed.

For each relevant rule, report:
- ✓ Compliant items (brief)
- ✗ Violations with file and line reference

### 4. Verification Reminder

If any `*-review.md` file defines verification commands, remind the user:

```
Verification commands (from python-cli-review.md):
  uv run pytest
```

Do NOT run the commands automatically — the user decides when to run them.

## Scoping

Audit the **current diff only**, not the entire repo. This keeps the audit focused and token-efficient.

## Output Format

```
## cpc-audit

### Rules Loaded
  6 files from .claude/rules/

### Changes
  Staged: 2 files
  Unstaged: 1 file

### Findings

**universal-coding-code-structure.md**
  ✓ Functions under length limits
  ✗ src/foo.py:42 — 4 levels of nesting (max 3)

**python-cli-best-practices.md**
  ✓ Path parameters used correctly
  ✓ Specific exceptions

### Verification
  Run: uv run pytest
```
