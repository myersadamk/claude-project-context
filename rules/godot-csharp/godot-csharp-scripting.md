---
paths:
  - "**/*.cs"
---

# Godot C# — Scripting

For C# scripts in a Godot 4 .NET project. The 3.x C# API differs (no source generators, different signal syntax); don't apply 3.x answers.

## Classes

- Every class deriving from `GodotObject` (so every `Node` and `Resource` script) MUST be `partial`. Godot's source generators write the other half (`GD0001` otherwise).
- One script class per file. The file name MUST match the class name exactly, including case, or Godot can't attach it.
- Use the generated `SignalName`, `MethodName` and `PropertyName` members instead of strings. Engine methods called by name are snake_case (`"add_child"`), which is the bug those members prevent.

## Signals and Events

- Declare signals as `[Signal] public delegate void HitEventHandler(...)` (the `EventHandler` suffix is required) and emit with `EmitSignal(SignalName.Hit, ...)`. Arguments MUST be Variant-compatible.
- Godot disconnects a signal automatically when the *emitter* is freed. It does NOT disconnect when the *receiver* is freed if the handler is a capturing lambda or the signal was connected with `+=`. Plain C# `event`s never auto-disconnect.
- So every `+=` on a longer-lived object MUST have a matching `-=` in `_ExitTree`, with the delegate kept in a field (a lambda can't be removed). Otherwise the next emit calls into a freed node and throws `ObjectDisposedException`.
- Plain C# `event`s are fine between C# objects. Use `[Signal]` when the editor, GDScript or `Connect` flags (`OneShot`) need to see it.

## Node References and Lifetime

- Get child nodes once, in `_Ready`, into fields. MUST NOT call `GetNode` or `FindChild` per frame. `%UniqueName` lookups work only inside the scene that owns the node.
- Prefer `[Export]` node and resource references over string paths when the editor wires them. Exports must be Variant-compatible; ranges are `[Export(PropertyHint.Range, "0,10,0.1")]` (C# has no `[ExportRange]`).
- Free nodes with `QueueFree()`. When the tree must be correct in the same frame, `RemoveChild` first, then `QueueFree()`.
- A freed object isn't `null`. Check `GodotObject.IsInstanceValid(obj)`. MUST NOT call `Dispose()` on Resources or other RefCounted objects that something else may still use.

## The Interop Boundary

Every call into the engine crosses from managed to native code. Most of the cost is marshalling, so:

- Copy an engine property into a local when it's read or changed more than once, and write it back once (`var p = Position; …; Position = p;`).
- MUST NOT pass string literals where a `StringName` or `NodePath` is expected in per-frame code: each call converts and allocates. Keep `static readonly StringName` fields for input actions and other names.
- MUST use .NET collections for game data. Every operation on a `Godot.Collections.Array` or `Dictionary` marshals, and LINQ over one marshals every element. When an engine call returns one, copy it into a .NET array once and reuse that array.
- Avoid `Variant` except for untyped engine APIs. A value type in a `Variant` is boxed.

## Frames, Physics and Precision

- Game state changes in `_PhysicsProcess` (fixed rate). `_Process` only draws: interpolation, animation, UI.
- Use one interpolation scheme per object. Either enable engine physics interpolation and call `ResetPhysicsInterpolation()` after spawning or teleporting, or interpolate by hand with `Engine.GetPhysicsInterpolationFraction()` between a simulation's previous and current state.
- Godot physics isn't deterministic, and `Vector3`/`Transform3D` are single precision by default. Deterministic rules MUST NOT depend on Godot physics or engine math. Convert simulation doubles to engine floats only at the presentation boundary.

## Tool Scripts

- Avoid `[Tool]` C# scripts. Tool code runs in the editor, with no undo, and can crash it.
- Where one is needed, guard every side effect with `Engine.IsEditorHint()`. MUST NOT capture variables in Callables or Tween lambdas, or keep static caches (including JSON serializer caches), in tool code: they stop the editor from unloading the assembly, and C# stays broken until a restart.
