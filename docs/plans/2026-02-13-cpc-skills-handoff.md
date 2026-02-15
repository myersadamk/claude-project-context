# Handoff: cpc:init / cpc:audit Skills Branch

## What Was Done

Branch `feat/cpc-skills` (PR #3) implements:

1. **Stack-specific review rules** — `typescript-web-review.md` and `python-cli-review.md`, each with their own verification commands
2. **Refactored `universal-review.md`** — stack-agnostic, no more hardcoded npm commands
3. **`cpc:audit` skill** (`skills/cpc-audit/SKILL.md`) — reloads rules into context, audits current diff
4. **`cpc:init` skill** (`skills/cpc-init/SKILL.md`) — generates CLAUDE.md from installed review rules
5. **Updated `config.yaml`** — both skills added to all profiles
6. **Updated `README.md`** — documented everything

All 11 tests pass. Design doc at `docs/plans/2026-02-13-cpc-skills-design.md`.

## What Remains

### 1. Merge PR #3

```bash
cd /Users/koi/Repositories/myersadamk/claude-project-context
gh pr merge 3 --merge
git pull
git branch -d feat/cpc-skills
```

**Expect a config.yaml conflict.** Main changed the skills path to `../../github/claude-skills` but the branch had `../claude-skills`. Keep main's path (`../../github/claude-skills`) and add the new `cpc-audit` / `cpc-init` skills to each profile.

### 2. Fix `resolve_skill` for plugin-repo-structured skills

**Bug:** `interface-design` skill exists at `/Users/koi/Repositories/github/claude-skills/interface-design/` but `resolve_skill` can't find it because it only checks `entry/SKILL.md`. The actual SKILL.md lives at `entry/.claude/skills/interface-design/SKILL.md` (plugin repo structure).

**File:** `src/cpc/config.py`, lines 146-156

**Current code:**
```python
def resolve_skill(name: str, sources: list[SkillSource]) -> Path | None:
    for source in sources:
        if not source.path.is_dir():
            continue
        for entry in source.path.iterdir():
            if entry.is_dir() and entry.name.lower().replace("-", "").replace("_", "") == name.lower().replace("-", "").replace("_", ""):
                if (entry / "SKILL.md").exists():
                    return entry
    return None
```

**Fix:** Add a fallback check for the nested `.claude/skills/<name>/SKILL.md` path:
```python
                if (entry / "SKILL.md").exists():
                    return entry
                nested = entry / ".claude" / "skills" / entry.name / "SKILL.md"
                if nested.exists():
                    return entry
```

**Test this with:** `uv run cpc install --profile=astro-web /path/to/test-project` — should find both `vibesec` and `interface-design`.

### 3. Run cpc on self

After merging and fixing, run:
```bash
uv run cpc update .
uv run cpc status .
uv run pytest -v
```

## Session Note

The shell broke mid-session because the worktree at `.worktrees/feat-cpc-skills` was removed while it was the bash process's CWD. The worktree itself was successfully removed — only the shell process was affected.
