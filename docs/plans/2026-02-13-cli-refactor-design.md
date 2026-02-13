# CLI Refactor — Design Document

Date: 2026-02-13

## Problem

`install.py` is a single-purpose script that only manages rules. Skills
management is imminent, the CLI needs subcommands, and the output should
be readable. Raw `argparse` + `print` won't scale.

## Goals

1. Refactor to `click` + `rich` CLI managed by `uv`
2. Unified YAML config for rule sets AND skill sources
3. Declarative profiles (one profile = one project type's full context)
4. Subcommand structure that accommodates skills without further refactoring
5. Safety-focused test suite for filesystem operations
6. Deprecate the adjacent `claude-skills` install script — consolidate here

## Config model

```yaml
# config.yaml
sources:
  skills:
    - path: skills/                          # local to this repo
    - path: ../claude-skills                 # external repo
      update: git -C ../claude-skills pull   # optional: how to refresh

profiles:
  astro:
    rules:
      - universal
      - typescript-web
      - astro
    skills:
      - vibesec
      - interface-design

  nextjs:
    rules:
      - universal
      - typescript-web
      - nextjs
    skills:
      - vibesec
      - interface-design

  backend-java:
    rules:
      - universal
      - java-spring
    skills: []
```

### Rules resolution

Rules always come from `rules/` in this repo. Each rule set is a
subdirectory. All `.md` files in a set get symlinked.

### Skills resolution

Skills are resolved by name across all `sources.skills` paths. Each
skill is a directory containing at least a `SKILL.md`. First match wins
when scanning sources in order.

### Source updates

Sources with an `update` field can be refreshed via `cpc update`. The
value is a shell command executed from the repo root. Sources without
`update` are assumed to always be current (e.g., skills in this repo).

## CLI structure

```
cpc install <target> [--profile <name>]
cpc update  <target>
cpc status  <target>
```

### `install <target>`

First-time setup or profile change.

- If `--profile` given, applies it directly (non-interactive)
- If no `--profile`, presents available profiles for selection
- Creates `.claude/rules/` and `.claude/skills/` as needed
- Symlinks rules and skills per the profile
- Writes `.manifest.json`

### `update <target>`

Refresh existing installation.

- Reads `.manifest.json` for active profile
- Runs `update` commands on sources that define them
- Re-applies symlinks (picks up new/removed files)
- Cleans stale symlinks

### `status <target>`

Show what's installed.

- Lists active profile, rule sets, skills
- Checks symlink health (broken links)

### Manifest v2

```json
{
  "source": "/Users/koi/.../claude-project-context",
  "profile": "astro",
  "rules": ["universal", "typescript-web", "astro"],
  "skills": ["vibesec", "interface-design"],
  "installed": "2026-02-13"
}
```

## Project structure

```
claude-project-context/
├── pyproject.toml
├── src/
│   └── cpc/
│       ├── __init__.py
│       ├── cli.py           # click command definitions
│       ├── config.py        # YAML config loading + validation
│       ├── linker.py        # symlink logic
│       └── console.py       # rich console + logging helpers
├── config.yaml
├── rules/                   # (unchanged)
├── skills/                  # custom skills (new)
├── tests/
│   └── test_linker.py
├── docs/
│   └── plans/
└── README.md
```

### Dependencies

- `click` — CLI framework with subcommands
- `rich` — colored output, tables, status lines
- `pyyaml` — config file parsing
- `pytest` — test runner (dev dependency)

### Invocation

```bash
uv run cpc install /path/to/project
uv run cpc install /path/to/project --profile astro
uv run cpc update /path/to/project
uv run cpc status /path/to/project
```

Entry point: `[project.scripts] cpc = "cpc.cli:main"`

## Type model

All data structures use modern Python typing (3.11+). No `Any`, no untyped
dicts flowing through the system.

### Core types (`config.py`)

```python
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path


class RuleSet(StrEnum):
    """Available rule set names, matching rules/ subdirectories."""
    UNIVERSAL = "universal"
    TYPESCRIPT_WEB = "typescript-web"
    ASTRO = "astro"
    NEXTJS = "nextjs"
    JAVA_SPRING = "java-spring"


@dataclass(frozen=True)
class SkillSource:
    """A directory that contains skills."""
    path: Path
    update: str | None = None


@dataclass(frozen=True)
class Profile:
    """A named combination of rule sets and skills for a project type."""
    name: str
    rules: list[RuleSet]
    skills: list[str]


@dataclass(frozen=True)
class Config:
    """Top-level config parsed from config.yaml."""
    skill_sources: list[SkillSource]
    profiles: dict[str, Profile]


@dataclass(frozen=True)
class Manifest:
    """Recorded state of an installation, written to .manifest.json."""
    source: Path
    profile: str
    rules: list[RuleSet]
    skills: list[str]
    installed: str
```

### Linker result types (`linker.py`)

```python
class LinkAction(StrEnum):
    """What happened to a single file during install."""
    LINKED = "linked"
    UPDATED = "updated"
    SKIPPED = "skipped"
    CLEANED = "cleaned"


@dataclass(frozen=True)
class LinkResult:
    """Outcome for a single file."""
    filename: str
    action: LinkAction
    target: Path | None = None  # symlink target, None for cleaned


@dataclass(frozen=True)
class InstallResult:
    """Full outcome of an install or update operation."""
    target_dir: Path
    profile: str
    results: list[LinkResult]

    @property
    def linked(self) -> list[LinkResult]:
        return [r for r in self.results if r.action == LinkAction.LINKED]

    @property
    def updated(self) -> list[LinkResult]:
        return [r for r in self.results if r.action == LinkAction.UPDATED]

    @property
    def skipped(self) -> list[LinkResult]:
        return [r for r in self.results if r.action == LinkAction.SKIPPED]

    @property
    def cleaned(self) -> list[LinkResult]:
        return [r for r in self.results if r.action == LinkAction.CLEANED]
```

### Typing conventions

- `frozen=True` on all dataclasses — config and results are immutable
- `StrEnum` for closed sets of string values — IDE autocomplete, exhaustive matching
- `Path` not `str` for all filesystem paths
- `str | None` union syntax (3.10+), not `Optional[str]`
- No `TypedDict` — dataclasses are more explicit and support methods
- Functions declare return types; `linker.py` functions return `InstallResult`,
  not raw dicts or tuples

### RuleSet enum maintenance

`RuleSet` is the one type that must stay in sync with the `rules/`
directory. When a new rule set directory is added, add a corresponding
enum member. This is intentional friction — it forces you to acknowledge
the new set in the type system rather than silently discovering it.

If this proves too rigid (e.g., users want to add rule sets without
touching Python), it can be relaxed to a validated `str` with runtime
checks against the filesystem. Start strict, loosen if needed.

## Test strategy

Focus on `linker.py` — the only module that touches the filesystem
destructively. All tests use real filesystem operations against `tmp_path`.

### Safety invariants

These are the critical tests. If any of these fail, the tool is dangerous.

- `test_never_deletes_non_symlink_files` — local overrides are sacred
- `test_never_overwrites_non_symlink_files` — same, for the install path
- `test_stale_cleanup_only_removes_our_symlinks` — don't break other tools
- `test_only_writes_inside_claude_directory` — no operations outside target

### Correct behavior

- `test_creates_symlinks_for_selected_rules`
- `test_creates_symlinks_for_selected_skills`
- `test_replaces_existing_symlinks`
- `test_cleans_stale_symlinks_on_update`
- `test_idempotent_reinstall`

### Error handling

- `test_nonexistent_source_path_errors`
- `test_nonexistent_profile_errors`
- `test_missing_manifest_on_update_errors`

## Implementation path

1. Create `pyproject.toml` with `uv`, declare dependencies and entry point
2. Create module structure (`src/cpc/`)
3. Write `config.yaml` with current profiles
4. Extract symlink logic from `install.py` into `linker.py`
5. Write `console.py` (rich console wrapper)
6. Write `config.py` (YAML loading, profile/source resolution)
7. Write `cli.py` (click commands: install, update, status)
8. Write `test_linker.py` (safety invariants first)
9. Delete old `install.py`
10. Update README.md
11. Verify against both projects
