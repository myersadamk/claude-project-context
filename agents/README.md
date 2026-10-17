# Agent Library

A collection of Claude Code subagent definitions for common workstream types. Drop any file into `~/.claude/agents/` and it is immediately available to any CC session.

## Agent Index

| File | Model | Effort | Purpose |
|---|---|---|---|
| `general-max.md` | opus | max | Unconstrained — hardest open-ended problems |
| `general-high.md` | opus | high | Hard non-coding tasks, complex reasoning |
| `general-med.md` | sonnet | medium | General tasks, nothing specialized |
| `general-low.md` | haiku | low | Quick tasks, low stakes |
| `coding-high.md` | opus | high | Difficult features, complex refactors |
| `coding-med.md` | sonnet | medium | Everyday implementation |
| `research-max.md` | opus | max | Deep open-ended investigation |
| `research-high.md` | sonnet | high | Standard codebase/doc investigation |
| `review-code-high.md` | sonnet | high | Reviewing others' work — design, correctness |
| `review-spec-low.md` | haiku | low | Mechanical spec/checklist compliance |
| `git-ops-low.md` | haiku | low | Safe git ops — status, log, commit |
| `git-ops-high.md` | sonnet | high | Risky git ops — rebase, reset, force-push |

## When to Use Which

**general-\***: Catch-all agents. Reach for these when no specialized agent fits. Use `-low` for quick questions or simple fixes, `-med` for standard tasks, `-high` for hard reasoning problems, `-max` when you need everything.

**coding-\***: Implementation work. `-med` covers most days. Upgrade to `-high` when the problem is genuinely hard — complex refactor, difficult bug, architectural decision.

**research-\***: Read-only investigation. Neither agent can modify files. Use `-high` for standard codebase exploration and doc lookup. Use `-max` for deep, open-ended research where you need opus-level synthesis.

**review-\***: Code review. `review-code-high` for thoughtful review of others' work — it evaluates design and correctness, not just style. `review-spec-low` for fast mechanical checking against an explicit spec or checklist (always supply the criteria upfront).

**git-ops-\***: Git operations. `git-ops-low` for routine safe operations. `git-ops-high` for anything destructive or complex — it confirms before acting and prefers `--force-with-lease`.

## Deployment

First time:

```bash
mkdir -p ~/.claude/agents/
cp agents/[^R]*.md ~/.claude/agents/
```

To deploy a single agent:

```bash
cp agents/research-high.md ~/.claude/agents/
```

To update after pulling changes:

```bash
cp agents/[^R]*.md ~/.claude/agents/
```

> **Note:** The `[^R]` glob excludes `README.md` — CC would attempt to parse it as an agent definition otherwise. The update command overwrites any local edits in `~/.claude/agents/`. This repo is the source of truth. Customize agents here and commit the change rather than editing `~/.claude/agents/` directly.

## Naming Convention

Files follow `<purpose>-<effort>.md`. The filename suffix maps to the frontmatter `effort:` field:

| Suffix | Frontmatter value | Typical model |
|---|---|---|
| `-max` | `max` | opus |
| `-high` | `high` | opus (coding) / sonnet (research, review) |
| `-med` | `medium` | sonnet |
| `-low` | `low` | haiku |

## How Routing Works

The `description` frontmatter field is the routing signal. When a parent CC session uses the `Agent` tool to dispatch subagents, it reads each agent's description to decide which one fits the task. A well-written description is effectively a routing rule.

Example: a parent session asked to "rebase this branch onto main" reads all available descriptions and routes to `git-ops-high` because its description explicitly lists rebase as its domain.

In your current workflow (manual tab switching), you select agents explicitly. Descriptions also serve as your human-readable reminder of which agent to reach for.

## Future: Orchestrator Pattern

The natural evolution of this library is an `orchestrator` agent that routes tasks automatically:

```
you
 └── orchestrator session
      ├── dispatches → research-high   (investigation)
      ├── dispatches → coding-med      (implementation)
      └── dispatches → review-code-high (review)
```

You interact with one session; it decomposes tasks and delegates to the right specialized agent. See `docs/superpowers/specs/2026-04-29-agents-design.md` for the full design.
