# cpc:init and cpc:audit Skills — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add cpc:init and cpc:audit skills and restructure review rules so verification commands are stack-specific, not hardcoded.

**Architecture:** Each rule set gets its own `*-review.md` with stack-appropriate verification commands. Two new skills (cpc:init, cpc:audit) are markdown-only SKILL.md files that guide Claude's behavior in conversation. No new Python code — this is entirely content and config.

**Tech Stack:** Markdown (SKILL.md format), YAML (config.yaml)

---

### Task 1: Create typescript-web-review.md

Extract the TypeScript-specific verification gate and review checklist from `universal-review.md` into its own file.

**Files:**
- Create: `rules/typescript-web/typescript-web-review.md`

**Step 1: Create the review file**

```markdown
# TypeScript Web — Review

## Verification Commands

All MUST pass before approval:

\`\`\`bash
npm run lint && npm run typecheck && npm run format:check && npm run test && npm run build
\`\`\`

Skip `build` only for documentation-only changes.

## Checklist

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

### Design System (-> local design-system.md)

- [ ] Colors use semantic tokens defined in design-system
- [ ] Spacing follows defined scale
- [ ] Typography matches defined families and scale
- [ ] Motion uses design-system duration and easing tokens
- [ ] Skip if design-system.md is not yet populated
```

**Step 2: Commit**

```bash
git add rules/typescript-web/typescript-web-review.md
git commit -m "feat: add typescript-web review rule with verification gate"
```

---

### Task 2: Create python-cli-review.md

**Files:**
- Create: `rules/python-cli/python-cli-review.md`

**Step 1: Create the review file**

```markdown
# Python CLI — Review

## Verification Commands

All MUST pass before approval:

\`\`\`bash
uv run pytest
\`\`\`

## Checklist

### CLI Patterns (-> python-cli-click.md)

- [ ] Click commands are thin — logic extracted into plain functions
- [ ] `click.Choice` for closed option sets, not manual validation
- [ ] `click.Path(path_type=Path)` on all path parameters
- [ ] `raise SystemExit(1)` for errors, not `sys.exit()`
- [ ] `rich` for output, not raw `print()`

### Typing (-> python-cli-typing.md)

- [ ] `NewType` for validated domain strings
- [ ] `@dataclass(frozen=True)` for structured data, no untyped dicts
- [ ] `Path` not `str` for filesystem values
- [ ] Explicit return types on all functions
- [ ] No `Any`

### Best Practices (-> python-cli-best-practices.md)

- [ ] Keyword-only args for functions with 3+ similar-typed parameters
- [ ] `relative_to()` for path ancestry checks, never string matching
- [ ] `is_symlink()` before `exists()` when handling symlinks
- [ ] Tests use real filesystem (`tmp_path`), no mocking
```

**Step 2: Commit**

```bash
git add rules/python-cli/python-cli-review.md
git commit -m "feat: add python-cli review rule with verification gate"
```

---

### Task 3: Refactor universal-review.md

Remove hardcoded npm commands and TypeScript-specific checklist items. Keep only stack-agnostic review concerns.

**Files:**
- Modify: `rules/universal/universal-review.md`

**Step 1: Replace contents with stack-agnostic version**

```markdown
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
```

**Step 2: Commit**

```bash
git add rules/universal/universal-review.md
git commit -m "refactor: make universal-review stack-agnostic, remove hardcoded npm commands"
```

---

### Task 4: Create cpc:audit skill

**Files:**
- Create: `skills/cpc-audit/SKILL.md`

**Step 1: Create directory and skill file**

The SKILL.md follows the Claude Code skill format. Directory stays `cpc-audit` (filesystem-safe), but the `name:` frontmatter uses `cpc:audit` for the namespaced invocation.

```markdown
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
```

**Step 2: Commit**

```bash
git add skills/cpc-audit/SKILL.md
git commit -m "feat: add cpc:audit skill for rule compliance checking"
```

---

### Task 5: Create cpc:init skill

**Files:**
- Create: `skills/cpc-init/SKILL.md`

**Step 1: Create directory and skill file**

```markdown
---
name: cpc:init
description: Generate or update CLAUDE.md with verification commands and profile metadata from installed cpc rules. Use when setting up a new project or after changing profiles.
---

# cpc:init

## When to Use

- After running `cpc install` on a new project
- After running `cpc update` when the profile changed
- When a project has no CLAUDE.md or its verification commands are wrong

## Steps

1. **Read the manifest:** Load `.claude/rules/.cpc.manifest.json` from the current project. If it doesn't exist, tell the user to run `cpc install` first and stop.

2. **Find review rules:** Read all files matching `*-review.md` in `.claude/rules/`. Extract the verification commands from each (the content inside the `Verification Commands` section's code block).

3. **Check for existing CLAUDE.md:** Read `CLAUDE.md` in the project root if it exists.

4. **Generate the cpc section:**

```markdown
<!-- cpc:start -->
## Verification

All must pass before committing:

\`\`\`bash
{extracted verification commands, one per review file}
\`\`\`

## Profile

Installed by [cpc](https://github.com/myersadamk/claude-project-context).
Profile: `{profile name}`
Rule sets: {comma-separated list}
<!-- cpc:end -->
```

5. **Write CLAUDE.md:**
   - If CLAUDE.md exists and contains `<!-- cpc:start -->` / `<!-- cpc:end -->` markers: replace only the content between the markers.
   - If CLAUDE.md exists but has no markers: append the cpc section at the end.
   - If no CLAUDE.md exists: create one with just the cpc section.

6. **Report:** Show the user what was written and where.

## Key Constraints

- NEVER delete or modify content outside the `<!-- cpc:start -->` / `<!-- cpc:end -->` markers
- Only read from `.claude/rules/` — never reference the source cpc repo
- If multiple review files have verification commands, combine them (each on its own line)
```

**Step 2: Commit**

```bash
git add skills/cpc-init/SKILL.md
git commit -m "feat: add cpc:init skill for CLAUDE.md generation"
```

---

### Task 6: Update config.yaml

Add cpc:audit and cpc:init to all profiles so they're installed alongside the rules.

**Files:**
- Modify: `config.yaml`

**Step 1: Add skills to profiles**

```yaml
sources:
  skills:
    - path: skills/
    - path: ../claude-skills
      update: git -C ../claude-skills pull

profiles:
  astro-web:
    rules:
      - universal
      - typescript-web
      - astro
    skills:
      - vibesec
      - interface-design
      - cpc-audit
      - cpc-init

  nextjs-web:
    rules:
      - universal
      - typescript-web
      - nextjs
    skills:
      - vibesec
      - interface-design
      - cpc-audit
      - cpc-init

  python-cli:
    rules:
      - universal
      - python-cli
    skills:
      - cpc-audit
      - cpc-init
```

**Step 2: Commit**

```bash
git add config.yaml
git commit -m "feat: add cpc:audit and cpc:init skills to all profiles"
```

---

### Task 7: Update README.md

Document the new skills and review file convention.

**Files:**
- Modify: `README.md`

**Step 1: Add skills section after the "Adding skills" section**

Add a new section documenting the two built-in skills and the review file convention. Key points:
- Each rule set can include a `*-review.md` with verification commands
- `cpc:init` generates CLAUDE.md from installed review rules
- `cpc:audit` reloads rules and checks recent changes

**Step 2: Update the rule sets table** to show the new review files.

**Step 3: Commit**

```bash
git add README.md
git commit -m "docs: document cpc:init, cpc:audit skills and review file convention"
```

---

### Task 8: Run cpc on self

Run `cpc install` or `cpc update` against this repo to verify the new skills and review files are discovered and linked correctly.

**Step 1: Run update**

```bash
uv run cpc update .
```

Expected: skills linked, review files present.

**Step 2: Verify**

```bash
uv run cpc status .
```

**Step 3: Run tests**

```bash
uv run pytest -v
```

Expected: All 11 existing tests pass (no new tests needed — this is all content, no Python code changes).
