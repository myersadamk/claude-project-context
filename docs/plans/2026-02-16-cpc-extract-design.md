# cpc-extract Skill Design

## Overview

A Claude Code skill that scans a repository's `.claude/rules/` and `.claude/skills/` for non-symlink files, generalizes their content (removing repo-specific references, replacing concrete code with pseudo-code), and integrates them into the cpc central repo's rule sets and profiles.

### What it is

- AI-mediated extraction — content is always generalized, never raw-copied
- Conversational — every extraction requires user approval
- Placement-aware — suggests best-fit existing rule sets based on content analysis

### What it is NOT

- Not a file copier
- Not a profile creator by default — prefers adding to existing rule sets
- Not automatic — user confirms every generalized file

### Prerequisites

- Must be run from within the cpc repo (or have access to it)
- Target repo must have a `.claude/` directory
- Reads `config.yaml` to understand existing rule sets and profiles

## Flow

### Phase 1: Discovery

1. Resolve the target repo path from the skill argument
2. Scan `.claude/rules/` for files that are NOT symlinks
3. Scan `.claude/skills/` for directories that are NOT symlinks
4. Cross-reference with `.cpc.manifest.json` if present (notes installed profile to inform placement suggestions)
5. Present summary of all findings:

```
Found 3 non-symlink items in ../astro-template/.claude/:

Rules:
  1. design-system.md — "Design System" (14 lines)
  2. deployment-checklist.md — "Deployment Checklist" (32 lines)

Skills:
  3. custom-linter/ — SKILL.md (28 lines)

Installed profile: astro-web (universal-coding, typescript-web, astro-web)

Process these one at a time? (y/n)
```

The manifest context helps make smart placement suggestions. If no manifest exists, the skill relies on content analysis alone.

### Phase 2: Per-Item Processing

For each item, follow this sequence:

**Step 1 — Read & Analyze.** Read file content. Identify repo-specific references: file paths, project names, specific tool configs, concrete code examples, references to other project files.

**Step 2 — Propose Placement.** Suggest the best-fit existing rule set based on content analysis and the installed profile's rule sets:

```
design-system.md — enforces design system discipline for UI work

Recommended: Add to typescript-web as typescript-web-design-system.md
  Reasoning: This is a web UI concern shared across all TS web projects.

Alternatives:
  - Create new rule set: web-design-system
  - Add to a different existing rule set
  - Skip
```

**Step 3 — Generalize & Present.** Show the proposed generalized content with a change summary:

```
Changes from original:
  - Removed reference to TEMPLATE_TODO.md (project-specific)
  - Kept interface-design skill references (these are cpc skills)

--- Proposed: rules/typescript-web/typescript-web-design-system.md ---
[generalized content here]
---
```

Generalization principles:
- Remove all repo-specific file paths and project names
- Replace concrete code examples with pseudo-code or generic examples
- Keep references to cpc-managed skills (these are portable)
- Preserve the rule's intent and enforcement language

**Step 4 — Confirm & Write.** User approves, requests edits, or skips. On approval, write the file.

### Phase 3: Config Update & Completion

**Config updates:** If new rule sets were created, update `config.yaml` — ask the user which profiles should include the new set, pre-selecting relevant ones based on the source repo's manifest. If files were only added to existing rule sets, no config change is needed.

**Summary:**

```
Extraction complete:

  <checkmark> design-system.md -> rules/typescript-web/typescript-web-design-system.md
  <checkmark> deployment-checklist.md -> rules/astro-web/astro-web-deployment.md
  <skip> custom-linter/ — skipped

Config changes: none (all added to existing rule sets)

Next steps:
  - Run `cpc update <target>` to sync the new rules back
  - The extracted files in the target repo will become symlinks on next update
```

**Optional: Run `cpc update`** on the source repo to replace original non-symlink files with symlinks to the newly centralized versions, completing the round-trip.
