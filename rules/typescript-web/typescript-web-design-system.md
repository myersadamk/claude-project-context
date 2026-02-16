# Design System

All work involving interface design, styling, or visual components MUST use
the `interface-design` skill. The canonical design system lives in
`.interface-design/system.md`, managed by that skill.

- Before starting UI/styling work, invoke `interface-design:init` (first time)
  or `interface-design:status` (ongoing)
- Prompt the user to invoke the skill if you detect styling work is needed
- MUST NOT hard-code design tokens — always reference the design system

If `.interface-design/system.md` does not exist yet, the project has not
completed design system setup. Run `interface-design:init` to initialize it.
