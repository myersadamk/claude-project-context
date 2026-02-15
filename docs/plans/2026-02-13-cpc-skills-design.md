# cpc:init and cpc:audit Skills

## Problem

`universal-review.md` hardcodes `npm run lint && npm run typecheck && ...` as the verification gate. This is wrong for non-TypeScript projects (e.g., Python CLI). There's also no bridge between shared rules and a project's `CLAUDE.md`, which is where project-specific instructions belong.

Rules loaded at conversation start drift out of context during long sessions. There's no way to "refresh" Claude's awareness of the installed rules.

## Design

### Rule Restructuring

Each rule set gets a `*-review.md` file containing:
- Verification commands appropriate to that stack
- Review checklist items specific to that stack

| Rule set | Review file | Verify command |
| --- | --- | --- |
| `universal` | `universal-review.md` | _(none — stack-agnostic checklist only)_ |
| `typescript-web` | `typescript-web-review.md` | `npm run lint && npm run typecheck && npm run format:check && npm run test && npm run build` |
| `python-cli` | `python-cli-review.md` | `uv run pytest` |
| `astro` | _(inherits from typescript-web)_ | — |
| `nextjs` | _(inherits from typescript-web)_ | — |

**`universal-review.md` changes:** Remove hardcoded npm commands. Keep the stack-agnostic checklist (Correctness, Security, Testing principles). Reference "verification commands from your stack's review rule" instead.

### cpc:init Skill

**Purpose:** Set up `CLAUDE.md` for a project with the correct verification gate and profile metadata.

**Trigger:** `/cpc:init` in a conversation

**Behavior:**
1. Read all `*-review.md` files from `.claude/rules/` in the current project
2. Extract verification commands from each review file
3. Read `.cpc.manifest.json` to identify the installed profile
4. Generate or update `CLAUDE.md`:
   - Verification section with the combined/correct commands
   - Profile metadata note
5. Use HTML comment delimiters (`<!-- cpc:start -->` / `<!-- cpc:end -->`) to mark the managed section
6. Preserve any user-written content outside the delimited section

**Key constraint:** Only reads from `.claude/rules/` — never references the source cpc repo. The target project is self-contained after install.

### cpc:audit Skill

**Purpose:** Reload installed rules into context and check recent changes against them.

**Trigger:** `/cpc:audit` in a conversation

**Behavior:**
1. Read every `.md` file in `.claude/rules/` (forces rules back into context)
2. Run `git diff --cached` and `git diff` to identify recent changes
3. Walk through each rule file and check the diff against it
4. Report a checklist of findings — compliant items and violations
5. If review files specify verification commands, remind the user to run them

**Scoping constraint:** Audit the current diff, not the entire repo. This keeps token usage reasonable (~5-8K for rules + diff) and findings actionable.

### Skill File Locations

```
skills/
  cpc:init/
    SKILL.md
  cpc:audit/
    SKILL.md
```

These are installed into target projects via the profile's `skills` list in `config.yaml`.

## Changes Required

1. **Create `python-cli/python-cli-review.md`** — verification: `uv run pytest`
2. **Create `typescript-web/typescript-web-review.md`** — verification: `npm run lint && npm run typecheck && npm run format:check && npm run test && npm run build`
3. **Refactor `universal-review.md`** — remove hardcoded npm commands, keep stack-agnostic checklist
4. **Create `skills/cpc:init/SKILL.md`** — skill definition
5. **Create `skills/cpc:audit/SKILL.md`** — skill definition
6. **Update `config.yaml`** — add cpc:init and cpc:audit to all profiles' skills lists
7. **Update `README.md`** — document the new skills and review file convention

## Token Cost Analysis

- **cpc:init:** One-time cost. Reads ~3-5 small files, writes one section. Negligible.
- **cpc:audit:** ~5-8K tokens to reload rules. Diff adds variable cost but is bounded by what the developer changed. Acceptable for a targeted compliance check.
