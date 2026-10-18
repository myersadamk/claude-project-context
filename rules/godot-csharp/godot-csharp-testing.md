---
paths:
  - "**/*.cs"
  - "**/*.tscn"
---

# Godot C# — Headless Testing

Rules decided by the engine are tested in the plain C# library (-> csharp-core-testing.md). In-engine tests check wiring: that the presentation reads the right state, builds the right nodes and survives the frame loop.

## Smoke Scenes

- A smoke test is a scene whose script checks something, prints one sentinel line (`<PROJECT>_SMOKE: PASS|FAIL …`) and quits with `GetTree().Quit(code)`, exit code 0 only on a pass.
- The runner MUST require all three: exit 0, a PASS line, and no timeout. Run each scene under `timeout`. A scene whose script failed to attach (missing assembly) idles forever instead of failing.
- MUST run `godot --headless --path <project> --import` once before the scenes, and build the C# project first. A fresh checkout has no import cache.
- Every scene in the smoke folder runs. Adding a test MUST NOT need an edit to the runner.

## Frames and Order

- MUST assert node counts and state **before** awaiting a frame. After an await, deferred frees (`QueueFree`) have run, so a leaked or double-freed node becomes invisible.
- Production code that discards a node MUST call `RemoveChild` and then `QueueFree`, so the tree is correct within the same frame.
- Injected input MUST be followed by `Input.FlushBufferedEvents()` before awaiting physics frames. Godot flushes buffered input once per main-loop iteration, and several physics frames can run in one iteration when the loop catches up.
- Code that steps the simulation synchronously MUST NOT await in between, or `_PhysicsProcess` will step it again with device input.
- Poses, animation mixers and transforms only update in a live tree: seek and advance from inside the scene, not from a `SceneTree` script's init.

## Time Is an Input

- MUST NOT assert on wall-clock seconds in smoke scenes. Count frames or physics ticks you step, or call the poll or reload method directly, and assert "within N frames/polls".
- Hot-reload and file-watcher tests MUST trigger the poll themselves (or step a known number of frames), not sleep and hope.
- The runner's per-scene `timeout` is a hang guard only (generous, about 10× normal). A scene that needs it to pass is broken.
- Frame-time and render cost are reported by benches, not asserted in the gate.

## Known Answers in the Engine

- Every mapping between engine space and simulation space (positions, yaw, scale) MUST have at least one hand-derived known-answer check. End-to-end checks that read back through the same mapping cancel its bugs out.
- The headless viewport is tiny (64×64), so aspect-dependent code is untested headless. Say so in the test, and leave that case to a human look.

## Debugging

- Save the full engine output of a failing run to a file and read it. MUST NOT add temporary prints to production code to debug a test.
- Visual and feel quality are never claimed from a headless pass. A pass proves wiring.

## Frameworks

- For larger in-engine suites, GoDotTest (Chickensoft) and GdUnit4 (gdUnit4Net) both run C# tests in headless Godot 4. A hand-rolled smoke runner is fine while the suite is small.
