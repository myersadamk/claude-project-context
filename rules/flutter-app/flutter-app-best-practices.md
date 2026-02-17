# Flutter App — Best Practices

## Widget Composition

- MUST prefer specific widgets (`DecoratedBox`, `Padding`, `SizedBox`, `ColoredBox`) over `Container`
- MUST use `SizedBox` for spacing between siblings, not empty `Container` or `Padding` wrappers
- MUST extract repeated widget subtrees into a named widget after 2 occurrences
- MUST use `const` constructors wherever possible
- MUST NOT nest more than 4 levels of widget indentation without extracting
- MUST NOT use `Container` when only one property is needed (use the specific widget instead)

## Naming

- Widgets: `PascalCase` — file name MUST match widget name (`project_card.dart` -> `class ProjectCard`)
- Files: `snake_case` for all Dart files
- Boolean variables: MUST prefix with `is`, `has`, `should`, or `show`
- Callback props: MUST prefix with `on` (`onTap`, `onSubmit`, `onChanged`)
- Private members: MUST prefix with `_`

## State Management

- MUST use the lowest-complexity solution that works:
  1. Stateless widget (no state needed)
  2. StatefulWidget (local UI state only)
  3. InheritedWidget / InheritedNotifier (shared state within subtree)
  4. State management package (complex cross-cutting state)
- MUST NOT lift state higher than necessary
- MUST NOT use global state for data that only one widget needs
- MUST dispose controllers, streams, and animation controllers in `dispose()`

## Imports

- MUST use package imports for project files (`package:myapp/...`), not relative imports
- MUST NOT use relative imports that climb more than one level (`../../` is banned)
- MUST group imports with a blank line between groups:
  1. Dart SDK (`dart:...`)
  2. Flutter SDK (`package:flutter/...`)
  3. External packages
  4. Project imports (`package:myapp/...`)

## Error Handling

- MUST only validate at system boundaries (user input, API responses, platform channels)
- MUST NOT add defensive try/catch around code that cannot throw
- MUST NOT add null checks for values guaranteed by the type system
- MUST use `Result` types or typed exceptions over generic `catch (e)`

## File Size

- MUST investigate extraction opportunities if a widget file exceeds 200 lines
- This is a smell threshold, not a hard limit — but it MUST trigger review

## Dependencies

- MUST NOT add new packages without explicit discussion
- MUST prefer Flutter SDK solutions over third-party packages
- MUST NOT add packages that duplicate SDK functionality

