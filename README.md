# claude-project-context

Shared Claude Code rules and skills for consistent engineering standards across projects. Manage rule sets and reusable skills from a single source, then install them into any project with one command.

## How it works

Rules and skills live here as markdown files organized by technology stack. The `cpc` CLI symlinks them into each project's `.claude/` directory. Edit once, propagate everywhere.

### Three layers

| Layer | Lives in | Example |
| --- | --- | --- |
| **Shared rules** | This repo (`rules/`) | `typescript-web-types.md` |
| **Project config** | Each project's `CLAUDE.md` | Commands, structure, deployment |
| **Local rules** | Each project's `.claude/rules/` (non-symlinked) | `design-system.md` |

### Rule sets

| Set | Files | Purpose |
| --- | --- | --- |
| `universal` | `universal-review.md`, `universal-security.md`, `universal-code-structure.md` | Quality gate, security baseline, readability |
| `typescript-web` | `typescript-web-types.md`, `typescript-web-tailwind.md`, `typescript-web-ui.md`, `typescript-web-best-practices.md`, `typescript-web-review.md` | TypeScript + Tailwind web projects |
| `astro` | `astro-framework.md`, `astro-testing.md` | Astro-specific patterns |
| `nextjs` | `nextjs-architecture.md`, `nextjs-mdx.md` | Next.js App Router + MDX |
| `python-cli` | `python-cli-best-practices.md`, `python-cli-click.md`, `python-cli-typing.md`, `python-cli-review.md` | Python CLI projects (uv, click, rich) |

### Composable combinations

| Project type | Sets |
| --- | --- |
| Next.js site | `universal` + `typescript-web` + `nextjs` |
| Astro site | `universal` + `typescript-web` + `astro` |
| Python CLI | `universal` + `python-cli` |

## Config

All profiles and skill sources are declared in `config.yaml` at the repo root.

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

  nextjs-web:
    rules:
      - universal
      - typescript-web
      - nextjs
    skills:
      - vibesec
```

**`sources.skills`** -- list of directories to search for skills. Each entry has a `path` (relative to the repo root or absolute) and an optional `update` command that runs during `cpc update` to refresh the source (e.g. `git pull`).

**`profiles`** -- named combinations of rule sets and skills. Each profile lists the rule sets to install and which skills to symlink. Profiles are what you select during `cpc install`.

## Install

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
# First time -- interactive profile selection
uv run cpc install /path/to/project

# Non-interactive -- specify profile by name
uv run cpc install /path/to/project --profile astro-web

# Re-apply from manifest and refresh sources
uv run cpc update /path/to/project

# Show what's installed
uv run cpc status /path/to/project
```

**`install`** -- symlinks rule files into `.claude/rules/` and skill directories into `.claude/skills/`. Prompts for a profile if `--profile` is not given. Writes `.cpc.manifest.json` recording the selection.

**`update`** -- reads `.cpc.manifest.json` from a previous install, runs any source `update` commands (e.g. `git pull`), then re-applies the same profile. Use this to pick up new or changed rules and skills without re-selecting.

**`status`** -- prints the installed profile, rule sets, skills, and checks symlink health. Reports any broken symlinks.

The installer:
- Symlinks selected rule files into the target's `.claude/rules/`
- Symlinks selected skill directories into the target's `.claude/skills/`
- Skips existing non-symlink files (local overrides are preserved)
- Replaces existing symlinks on re-run
- Cleans stale symlinks from removed rules or skills

## Verification gate

Each rule set defines its own verification commands in a `*-review.md` file:

| Rule set | Review file | Commands |
| --- | --- | --- |
| `typescript-web` | `typescript-web-review.md` | `npm run lint && npm run typecheck && npm run format:check && npm run test && npm run build` |
| `python-cli` | `python-cli-review.md` | `uv run pytest` |

Run `/cpc:init` after installing to generate the correct commands in your project's `CLAUDE.md`.

## Adding rules

1. Create a new directory under `rules/` or add a file to an existing set
2. Prefix the filename with the set name: `<set>-<topic>.md`
3. Run `cpc update` against each project to pick up changes

## Adding skills

1. Create a new directory under `skills/` (or in any configured source path)
2. Add a `SKILL.md` file inside the directory -- this is required for the skill to be discovered
3. Reference the skill by directory name in a profile's `skills` list in `config.yaml`

To add an external skill source, add an entry to `sources.skills` in `config.yaml` with its path and an optional `update` command.

## Built-in skills

Two skills ship with cpc and are added to every profile:

| Skill | Trigger | Purpose |
| --- | --- | --- |
| `cpc:init` | `/cpc:init` | Generate or update `CLAUDE.md` with verification commands and profile metadata from installed rules |
| `cpc:audit` | `/cpc:audit` | Reload all rules into context and audit recent changes against them |

### cpc:init

Run after `cpc install` or when a project has no `CLAUDE.md`. Reads `*-review.md` files from `.claude/rules/` to extract verification commands, then generates a managed section in `CLAUDE.md` delimited by `<!-- cpc:start -->` / `<!-- cpc:end -->` markers.

### cpc:audit

Run before a PR or when rules have drifted out of context during a long session. Re-reads every rule file in `.claude/rules/`, diffs recent changes, and reports a compliance checklist with specific file:line references.

### Review file convention

Each rule set can include a `*-review.md` file with stack-specific verification commands and a review checklist. These are what `cpc:init` reads to generate `CLAUDE.md` and what `cpc:audit` uses for compliance checking.

## Local overrides

If a project needs to override a shared rule, create a non-symlink file with
the same name. The installer will skip it and print a warning. To revert
to the shared version, delete the local file and re-run install.
