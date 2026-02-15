# cpc-audit rule set filtering

## Problem

In multi-stack projects (e.g. a Flutter app with a Python script), `/cpc-audit` loads all installed rules and audits against all of them. When a PR only touches Python files, Flutter rule findings are noise. There's no way to scope the audit to a subset of rule sets.

## Solution

Accept optional rule set names as arguments: `/cpc-audit python-cli`. The skill filters loaded rules to only files matching the given prefixes, plus `universal-coding` (always included).

## Design

### Filtering logic

- **No arguments** — load all `.md` files in `.claude/rules/` (current behavior, unchanged)
- **With arguments** — parse `$ARGUMENTS` as space-separated rule set names. Always include `universal-coding`. Load only files whose name starts with `<rule-set>-` for one of the resolved set names.

Examples:
- `/cpc-audit python-cli` — loads `universal-coding-*.md` + `python-cli-*.md`
- `/cpc-audit typescript-web astro-web` — loads `universal-coding-*` + `typescript-web-*` + `astro-web-*`
- `/cpc-audit` — loads everything (backward compatible)

### Warning on empty matches

If a prefix matches zero files, warn and skip:
```
No rules found for 'flutter-mobile' — skipping
```

### SKILL.md changes

1. Add `argument-hint: [rule-set...]` to frontmatter
2. Update step 1 (Reload Rules) with conditional filtering logic
3. Steps 2-4 unchanged — they operate on whatever rules were loaded

### What doesn't change

- No new files or scripts
- No config.yaml or manifest lookup
- No changes to audit logic, diff detection, or output format
- Default (no args) behavior identical to today

## Alternatives considered

| Approach | Rejected because |
|---|---|
| Profile name lookup via config.yaml | Requires access to cpc source repo; couples skill to config structure |
| Filter by reading manifest | Manifest records installed profile, not available rule sets; adds complexity |
| Change default behavior to suggest profiles | Adds noise to the common case; `argument-hint` provides sufficient discoverability |
