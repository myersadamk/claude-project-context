# Design System

All work involving interface design, styling, or visual components MUST use
the `flutter-interface-design` skill. The canonical design system lives in
`.interface-design/system.md`, managed by that skill.

- Before starting UI/styling work, invoke `flutter-interface-design` (first time)
  or read `.interface-design/system.md` (ongoing)
- Prompt the user to invoke the skill if you detect styling work is needed
- MUST NOT hard-code design tokens — always reference ThemeExtension fields
- MUST NOT use inline `Color()` literals in widget code — map to ColorScheme or ThemeExtension

If `.interface-design/system.md` does not exist yet, the project has not
completed design system setup. Invoke `flutter-interface-design` to initialize it.
