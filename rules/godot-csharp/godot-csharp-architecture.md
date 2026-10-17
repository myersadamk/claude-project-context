---
paths:
  - "**/*.cs"
  - "**/*.tscn"
---

# Godot C# — Architecture

## The Engine Presents; a Library Decides

- Game rules (damage, movement, AI, generation, loot) MUST live in a plain C# library with no Godot reference, tested with `dotnet test`. Godot code reads that library's state and sends it commands; it MUST NOT decide outcomes.
- Input MUST become commands (`Move`, `UseSkill`, `Dodge`) before it reaches the rules. Gameplay never reads devices directly. Latch edge presses (a press can arrive on a frame with no physics tick); sample holds on the tick.
- Entities MUST be identified by the library's stable ids. The presentation keeps a map from id to visual. MUST NOT use node paths, node names or instance ids as identity.
- Godot physics may drive presentation-only effects (debris, ragdolls). It MUST NOT feed back into the rules.

## Scenes

- Design scenes to have no dependencies on their surroundings. A parent provides what a child needs (a reference, a `Callable`, a `Bind(...)` call). A child reports what happened through a signal or event, upward, and never reaches up the tree or across to a sibling. The common ancestor wires siblings together.
- Keep one composition root per running scene: the top script that creates the services and binds the children. Children don't find their dependencies themselves.
- Reusable scenes MUST NOT depend on their path in the tree. `GetNode("../../X")` is a hidden dependency.

## Global State

- Use an autoload only for a broad system that owns its own data (audio, save, settings). An autoload that holds or edits other objects' data is global mutable state, with the bugs that brings.
- Prefer passing a reference over a singleton, and a `static` member over an autoload, when no node is needed.

## Data and Tuning

- Content and tuning are data files on shared schemas, loaded and validated by the library.
- Tuning SHOULD hot-reload. A file that fails validation keeps the last good values and shows the error. MUST NOT fall back to hidden built-in defaults.

## Further Reading

Chickensoft's layered architecture (visual nodes → state machines → pure logic → data, each coupled only to the layer below), its LogicBlocks state machines and AutoInject dependency provision are a well-documented C# take on the same split. Adopt them by decision, not by default.
