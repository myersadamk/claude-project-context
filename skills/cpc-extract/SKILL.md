---
name: cpc-extract
description: Use when extracting non-symlink rules or skills from a target repo into the cpc central repo. Scans .claude/ for local files, generalizes their content, and integrates them into existing rule sets and profiles.
argument-hint: "<path-to-repo>"
user-invocable: true
disable-model-invocation: true
---

# cpc-extract

Extract non-symlink rules and skills from a target repo, generalize them, and integrate into cpc's centralized rule sets.

## Why This Exists

Projects accumulate local `.claude/rules/` and `.claude/skills/` files that aren't managed by cpc. These represent proven patterns worth sharing across projects — but they contain repo-specific references that must be generalized before centralizing.

## Process

### 1. Resolve Target

Parse `$ARGUMENTS` as the path to a target repository. Resolve to absolute path.

If no argument provided, ask the user for the target repo path.

Verify the target has a `.claude/` directory. If not, stop with an error.

### 2. Discover Non-Symlink Items

Scan the target's `.claude/` directory:

- **Rules:** Find all files in `.claude/rules/` that are NOT symlinks. Use Glob to find files, then check each with a stat or readlink test.
- **Skills:** Find all directories in `.claude/skills/` that are NOT symlinks.

If a `.cpc.manifest.json` exists, load it to identify the installed profile. This context helps inform placement suggestions.

If nothing is found, report "No non-symlink items found" and stop.

### 3. Present Findings

List all discovered items before processing:

```
Found N non-symlink items in <target>/.claude/:

Rules:
  1. design-system.md — "Design System" (14 lines)
  2. deployment-checklist.md — "Deployment Checklist" (32 lines)

Skills:
  3. custom-linter/ — SKILL.md (28 lines)

Installed profile: astro-web (universal-coding, typescript-web, astro-web)
```

Ask the user to confirm before processing.

### 4. Process Each Item

For each item, one at a time:

#### Step A — Read & Analyze

Read the file content. Identify repo-specific references:
- File paths referencing the target project
- Project-specific names or identifiers
- Concrete code examples from the repo
- References to project-specific files (e.g. `TEMPLATE_TODO.md`, `package.json` paths)
- Tool configurations specific to the repo

#### Step B — Propose Placement

Read `config.yaml` to understand existing rule sets and profiles. Based on the file's content and the installed profile, suggest the best-fit existing rule set:

```
design-system.md — enforces design system discipline for UI work

Recommended: Add to typescript-web as typescript-web-design-system.md
  Reasoning: This is a web UI concern shared across all TS web projects.

Alternatives:
  - Create new rule set: web-design-system
  - Add to a different existing rule set
  - Skip
```

**Naming convention:** Files in a rule set follow the pattern `<rule-set>-<topic>.md` (e.g. `typescript-web-design-system.md`).

Wait for user to confirm or choose an alternative.

#### Step C — Generalize & Present

Write a generalized version of the content. Follow these principles:
- Remove all repo-specific file paths and project names
- Replace concrete code examples with pseudo-code or generic examples
- Keep references to cpc-managed skills (these are portable)
- Preserve the rule's intent and enforcement language
- Do NOT water down the rule — keep it prescriptive

Present the proposed content with a change summary:

```
Changes from original:
  - Removed reference to TEMPLATE_TODO.md (project-specific)
  - Kept interface-design skill references (these are cpc skills)

--- Proposed: rules/typescript-web/typescript-web-design-system.md ---
[generalized content]
---
```

Wait for user to approve, request edits, or skip.

#### Step D — Write

On approval, write the file to the appropriate location in the cpc repo.

### 5. Update Config

After all items are processed:

- If any **new rule sets** were created, update `config.yaml` to add them to the appropriate profiles. Ask the user which profiles should include the new set, pre-selecting profiles based on the source repo's manifest.
- If files were only added to **existing rule sets**, no config change is needed.

### 6. Summary & Next Steps

```
Extraction complete:

  ✓ design-system.md → rules/typescript-web/typescript-web-design-system.md
  ✓ deployment-checklist.md → rules/astro-web/astro-web-deployment.md
  ⊘ custom-linter/ — skipped

Config changes: none (all added to existing rule sets)
```

Ask if the user wants to run `cpc install <target> --profile <profile>` (or `cpc update <target>` if already installed) to symlink the newly centralized rules into the target repo.

**Important:** After install/update, the original non-symlink files still exist alongside the new symlinks. cpc never deletes non-symlinks (local overrides are sacred). Offer to delete the original files for the user — they are now superseded by the centralized versions.

## Generalization Principles

The core value of extraction is generalization. A good extracted rule:

- Uses **no code samples from the source repo** — only pseudo-code or generic examples
- References **no project-specific files** — paths, configs, or identifiers
- Preserves **prescriptive language** — MUST, MUST NOT, ALWAYS, NEVER
- Keeps **references to cpc skills** — these are portable across projects
- Is **useful to any project** using the target rule set

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Raw-copying without generalizing | Always rewrite; never copy verbatim |
| Creating new rule sets when existing ones fit | Default to existing rule sets; only create new ones when content doesn't fit anywhere |
| Over-generalizing until the rule is toothless | Preserve prescriptive intent; generalize references, not requirements |
| Forgetting the naming convention | Files must be `<rule-set>-<topic>.md` |
