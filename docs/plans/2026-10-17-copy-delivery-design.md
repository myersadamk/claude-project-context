# Copy Delivery

> Status: proposal, not implemented. Install rules as committed copies instead of gitignored symlinks, for projects whose sessions run in git worktrees or need path-scoped rules.

## Problem

`cpc install` symlinks each rule into `.claude/rules/` and gitignores the links. That breaks in three cases, all of which hit a project run by Claude implementer sessions in worktrees (first seen on Holdfast, 2026-10-17):

1. **Worktrees don't get the rules.** `claude --worktree <id>` makes a fresh checkout of tracked files under `.claude/worktrees/<id>/`, and that session loads `CLAUDE.md` and `.claude/rules/` from the worktree. Gitignored links aren't there. Claude Code reads through untracked skills, agents and commands from the main checkout, but not rules ([worktrees docs](https://code.claude.com/docs/en/worktrees#what-worktrees-share-with-the-main-checkout)).
2. **The relative links break one level down.** `os.path.relpath` makes links like `../../../claude-project-context/rules/x.md`. Copied or committed into a worktree three directories deeper, they point at nothing. Tested on `/mnt/c` under WSL2.
3. **Symlinked rules outside the project are treated as external imports.** They load only after a one-time approval dialog at the start of an interactive session, and then **only the ones without `paths:` load** ([memory docs](https://code.claude.com/docs/en/memory#share-rules-across-projects-with-symlinks)). A background session can't show the dialog, and path-scoped shared rules never load at all.

## Proposal

```
cpc install <target> --profile=godot-csharp --copy
```

- `--copy` writes real files into `.claude/rules/` and records `"delivery": "copy"` plus each file's sha256 in the manifest. `update` and `uninstall` read the mode from the manifest.
- Copies are **committed**, not gitignored, so every worktree and clone has them. The manifest is committed too.
- **Local overrides stay sacred.** On `update`, a copy whose current hash matches the manifest is replaced with the new version. A copy whose hash differs was edited locally: skip it and warn, as for any non-symlink file today. Stale cleanup removes only copies whose hash still matches.
- Frontmatter passes through unchanged. Claude Code reads only `paths` from a rule's frontmatter, ignores other fields, and strips it before loading ([rules frontmatter reference](https://code.claude.com/docs/en/memory#rules-frontmatter-reference)). So cpc could add a `cpc-source:` line for provenance at no context cost.
- Symlink mode stays the default. Nothing changes for existing installs.

## Path-scoped shared rules

The `csharp-core`, `godot-csharp` and `python-tools` sets carry `paths:` frontmatter with project-agnostic globs (`**/*.cs`, `**/*.tscn`, `**/*.py`). They load only when Claude touches a matching file, which keeps them out of planning and orchestration sessions. **They need copy delivery** (reason 3 above). In symlink mode they never load. Their `-review.md` files have no `paths`, so the gate is always in context.

A later extension: let a project narrow a set's globs at install time (`--paths godot-csharp='game/**'`), which cpc writes into the copied frontmatter. Without it, a project with both a plain C# library and a Godot project loads the Godot rules whenever any `.cs` file is touched.

## Tests to add

- `--copy` creates regular files, not links, and writes their hashes to the manifest.
- `update` replaces an unmodified copy and skips a modified one with a warning.
- `uninstall` removes unmodified copies and keeps modified ones.
- No `.gitignore` section is written in copy mode.
