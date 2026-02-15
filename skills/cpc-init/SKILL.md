---
name: cpc-init
description: Use when setting up CLAUDE.md for a project after installing cpc rules. Generates the verification gate from installed review rules.
user-invocable: true
disable-model-invocation: true
---

# cpc-init

Generate or update this project's `CLAUDE.md` with the correct verification commands, based on the installed cpc review rules.

## Why This Exists

After `cpc install`, a project has rules in `.claude/rules/` but no `CLAUDE.md` verification gate. Without it, there's no single place that says "run these commands before you're done." This skill bridges that gap.

## Process

### 1. Discover Installed Review Rules

**Important:** Use the Glob or Read tools to find files in `.claude/rules/`. Do NOT use git commands (`git ls-files`, `git ls-tree`) — rule files are symlinks and may not be tracked by git.

Read all `*-review.md` files from `.claude/rules/` in the current project.

For each review file, extract the verification commands from the fenced code block under `## Verification Commands`. Example:

```markdown
## Verification Commands

All MUST pass before approval:

\`\`\`bash
uv run pytest
\`\`\`
```

→ Extracted command: `uv run pytest`

If multiple review files define commands, collect all of them.

### 2. Generate CLAUDE.md Section

Create or update `CLAUDE.md` at the project root. The managed section is delimited by HTML comments and contains only the verification commands:

```markdown
<!-- cpc:start -->
## Verification

Run before completing any task:

\`\`\`bash
uv run pytest
\`\`\`
<!-- cpc:end -->
```

### 3. Preserve User Content

- If `CLAUDE.md` exists and contains `<!-- cpc:start -->` / `<!-- cpc:end -->`, replace only the content between those delimiters.
- If `CLAUDE.md` exists but has no delimiters, prepend the managed section above the existing content with a blank line separating them.
- If `CLAUDE.md` does not exist, create it with just the managed section.

**Never modify content outside the delimiters.**

## Output

After writing, show the user:
1. Which review files were found
2. The verification commands extracted
3. Whether `CLAUDE.md` was created or updated
