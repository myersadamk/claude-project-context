# claude-project-context

Shared Claude Code rules for consistent engineering standards across projects.

## How it works

Rules live here as markdown files organized by technology stack. An install
script symlinks them into each project's `.claude/rules/` directory. Edit once,
propagate everywhere.

### Three layers

| Layer | Lives in | Example |
| --- | --- | --- |
| **Shared rules** | This repo (`rules/`) | `typescript-web-types.md` |
| **Project config** | Each project's `CLAUDE.md` | Commands, structure, deployment |
| **Local rules** | Each project's `.claude/rules/` (non-symlinked) | `design-system.md` |

### Rule sets

| Set | Files | Purpose |
| --- | --- | --- |
| `universal` | `universal-review.md`, `universal-security.md` | Quality gate, security baseline |
| `typescript-web` | `typescript-web-types.md`, `typescript-web-tailwind.md`, `typescript-web-ui.md`, `typescript-web-best-practices.md` | TypeScript + Tailwind web projects |
| `astro` | `astro-framework.md`, `astro-testing.md` | Astro-specific patterns |
| `nextjs` | `nextjs-architecture.md`, `nextjs-mdx.md` | Next.js App Router + MDX |

### Composable combinations

| Project type | Sets |
| --- | --- |
| Next.js site | `universal` + `typescript-web` + `nextjs` |
| Astro site | `universal` + `typescript-web` + `astro` |

## Install

```bash
# First time — interactive selection
python3 install.py /path/to/project

# Re-apply same sets (non-interactive)
python3 install.py /path/to/project --update

# Change selection — run without --update
python3 install.py /path/to/project
```

The script:
- Symlinks selected rule files into the target's `.claude/rules/`
- Skips existing non-symlink files (local overrides are preserved)
- Replaces existing symlinks on re-run
- Cleans stale symlinks from removed rules
- Writes `.manifest.json` recording selections

## Verification gate

All typescript-web projects must define these scripts in `package.json`:

| Script | Purpose |
| --- | --- |
| `lint` | Linter |
| `typecheck` | Type checker |
| `format:check` | Formatter check |
| `test` | Test suite |
| `build` | Production build |

The universal review rule enforces:

```bash
npm run lint && npm run typecheck && npm run format:check && npm run test && npm run build
```

## Adding rules

1. Create a new directory under `rules/` or add a file to an existing set
2. Prefix the filename with the set name: `<set>-<topic>.md`
3. Run `install.py --update` against each project to pick up changes

## Local overrides

If a project needs to override a shared rule, create a non-symlink file with
the same name. The install script will skip it and print a warning. To revert
to the shared version, delete the local file and re-run install.
