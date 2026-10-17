# Claude Project Context (cpc)

A centralized repository of coding rules, best practices, and skills for Claude Code. Profiles bundle rule sets (e.g. `universal-coding`, `python-cli`, `typescript-web`) and skills (e.g. `vibesec`, `cpc-audit`) for different project types, so they can be symlinked into any target repo's `.claude/` directory.

## How it works

- **Rule sets** live in `rules/<name>/` as `.md` files — coding standards, review checklists, and patterns.
- **Profiles** are defined in `config.yaml` — each profile combines rule sets and skills for a project type (e.g. `astro-web`, `python-cli`).
- **Skills** are sourced from `skills/` and external repos configured in `config.yaml`.
- The `cpc` CLI (`cpc install`, `cpc update`, `cpc status`) symlinks the selected profile's rules and skills into a target project's `.claude/` directory.

## Project structure

- `src/cpc/` — CLI tool (`click`-based), with config loading, symlinking, and status commands
- `rules/` — rule set directories (`universal-coding`, `python-cli`, `typescript-web`, `astro-web`, `nextjs-web`, `web-security`, `python-tools`)
- `skills/` — skill directories (sourced locally and from external repos)
- `config.yaml` — profile definitions and skill source configuration

<!-- cpc:start -->
## Verification

Run before completing any task:

```bash
uv run pytest
```
<!-- cpc:end -->
