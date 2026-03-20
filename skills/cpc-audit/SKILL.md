---
name: cpc-audit
description: Use when you want to check recent code changes against installed cpc rules. Reloads rules into context and audits the current diff.
argument-hint: "[commit] [rule-set...]"
user-invocable: true
disable-model-invocation: true
---

# cpc-audit

Reload installed rules into context and audit recent changes against them.

## Why This Exists

Rules loaded at conversation start drift out of context during long sessions. There's no way to "refresh" awareness of them — and no structured check that recent changes actually comply. This skill solves both problems in one pass.

## Process

### 1. Reload Rules

**Important:** Use the Glob or Read tools to find files in `.claude/rules/`. Do NOT use git commands (`git ls-files`, `git ls-tree`) — rule files are symlinks and may not be tracked by git.

Determine which rules to load based on `$ARGUMENTS`:

**No arguments** — read **every** `.md` file in `.claude/rules/`. This is the default behavior.

**With arguments** — parse `$ARGUMENTS` as space-separated rule set names. Always include `universal-coding` even if not listed. Load only files from `.claude/rules/` whose name starts with one of the resolved prefixes (e.g. `python-cli-*.md`, `universal-coding-*.md`).

If a prefix matches zero files, warn and skip it:
```
No rules found for 'flutter-mobile' — skipping
```

Skip non-rule files (e.g. dotfiles) in either mode.

List what was loaded:
```
Loaded 6 rules (filtered by: python-cli):
  universal-coding-code-structure.md
  universal-coding-review.md
  universal-coding-security.md
  python-cli-best-practices.md
  python-cli-click.md
  python-cli-review.md
```

When no filter is active, omit the parenthetical:
```
Loaded 6 rules:
  ...
```

### 2. Identify Changes

**If `$ARGUMENTS` contains `commit`** — audit the most recent commit (`git diff HEAD~1`). Remove `commit` from the argument list before parsing rule-set filters.

**Otherwise** — audit the working tree:
```bash
git diff --cached
git diff
```

If both are empty, report "No changes to audit — use `cpc-audit commit` to audit the last commit" and stop.

If there are staged and unstaged changes, audit both — note which is which.

### 3. Audit Against Rules

Walk through each loaded rule file. For each rule that is relevant to the changed files, check compliance.

**Be specific.** Don't check TypeScript rules against Python files. Don't check Tailwind rules if no CSS/markup changed. Match rules to the files that changed.

For each relevant rule, report:
- ✓ Compliant items (brief)
- ✗ Violations with file and line reference

### 4. Run Verification Commands

If any `*-review.md` file defines verification commands, run them and report the results.

Extract commands from the fenced code block under `## Verification Commands` in each loaded review file. Run each command and include the output in the audit report.

If a command fails, flag it clearly in the findings.

## Scoping

Audit the **current diff** for line-level rule compliance. This keeps the audit focused and token-efficient.

However, some rules define **project-wide invariants** — requirements that must hold regardless of what changed (e.g. "base layout MUST include `<ClientRouter />`", "every page MUST have a meta description"). After auditing the diff, scan loaded rules for MUST statements that apply project-wide. For each one, verify the invariant holds — even if the relevant file is not in the diff. Report these under a separate **Project-Wide Invariants** section in the findings.

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
  ✓ uv run pytest — 11 passed
```
