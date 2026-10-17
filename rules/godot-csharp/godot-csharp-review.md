# Godot C# — Review Checklist

## Verification Commands

All MUST pass before approval, with `<project>` replaced by the folder that holds `project.godot`:

```bash
dotnet build <project> -warnaserror && godot --headless --path <project> --import
```

Then run every smoke scene headless, each under a timeout (-> godot-csharp-testing.md). A project SHOULD wrap the build, import and smoke run in one gate script and name it in its CLAUDE.md. Run it in a checkout the editor doesn't have open.

## Checklist

### Architecture (-> godot-csharp-architecture.md)

- [ ] No game rule decided in Godot code; input becomes commands
- [ ] Visuals keyed by the library's ids, never by node path or name
- [ ] Children don't reach up or across the tree; the parent wires them

### Scripting (-> godot-csharp-scripting.md)

- [ ] GodotObject classes are `partial`; file name matches class name
- [ ] Every `+=` has a `-=` in `_ExitTree`; no capturing lambdas on longer-lived emitters
- [ ] No `GetNode`, string `StringName`s, Godot collections, LINQ or allocations in per-frame code
- [ ] `QueueFree` (after `RemoveChild` where order matters); `IsInstanceValid`, not `null` checks
- [ ] State changes in `_PhysicsProcess`; `_Process` only draws

### Files (-> godot-csharp-files.md)

- [ ] `.uid` and `.import` files committed with their assets; no duplicated script `.uid`
- [ ] No whitespace-only editor churn mixed into the change
- [ ] Hand-edited `.tscn`/`.tres` load headless without errors or UID warnings

### Tests (-> godot-csharp-testing.md)

- [ ] Smoke scenes assert before awaiting; input flushed after injection
- [ ] Each engine↔simulation mapping has a hand-derived known answer
- [ ] Visual and feel quality left to a human
