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

   ```bash
   {extracted verification commands, one per review file}
   ```

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
