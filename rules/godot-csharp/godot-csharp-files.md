---
paths:
  - "**/*.tscn"
  - "**/*.tres"
  - "**/*.import"
  - "**/*.uid"
  - "**/project.godot"
  - "**/*.csproj"
  - "**/*.sln"
---

# Godot C# — Project Files and the Editor

Godot's scenes, resources and settings are text, so Claude can read and edit them. The editor writes them too, so every edit has two authors.

## What to Commit

- MUST commit `project.godot`, `.tscn`, `.tres`, `.import`, `*.uid`, the `.csproj` and the `.sln`. MUST ignore `.godot/` (the import cache) and the C# `bin/` and `obj/`.
- Godot 4.4+ writes a `.uid` file beside each script and shader, and scenes reference them by `uid://`. Move or rename a file together with its `.uid`. A lost `.uid` breaks references on other clones (Godot falls back to the path, with a warning).
- MUST NOT copy a script together with its `.uid`. The editor reassigns a duplicated UID for scenes and resources, but not for scripts. Duplicate in the editor, or delete the copied `.uid` and let the next import write a new one.
- Large binaries (models, textures, audio) go in Git LFS.

## Editing Text Resources by Hand

- Prefer building nodes in code or in the editor over hand-writing `.tscn` structure. Small edits (a property value, an `ext_resource` path) are fine. The editor drops comments and custom whitespace when it re-saves.
- Keep the header's `format=3`. `load_steps` is deprecated since 4.6; don't add or maintain it.
- `ext_resource` and `sub_resource` ids are strings referenced as `ExtResource("id")` and `SubResource("id")`. A new id MUST be unique in the file. A `uid=` MUST match the target's `.uid` file, or be left out.
- MUST NOT edit `.godot/`. Regenerate it with `godot --headless --path <project> --import`.
- After a hand edit, MUST load the scene headless (an import or a smoke run) and read the output for parse errors and UID warnings.

## The Editor Rewrites Files

- On load, the .NET plugin upgrades the `.csproj`: it rewrites `Sdk="Godot.NET.Sdk/<editor version>"` and raises the target framework to the engine's minimum. It also regenerates the csproj when no `.sln` contains the project. MUST keep a committed `.sln` beside the Godot project, pin one engine version, and diff the csproj after any upgrade.
- The built-in script editor indents with tabs by default, and converts a file's indentation on save. It doesn't read `.editorconfig`. Edit C# in an external editor, or set Editor Settings › Text Editor › Behavior › Indent › Type to Spaces. MUST check `git diff` for whitespace-only changes and MUST NOT commit them mixed with real changes.
- A shell session and a running editor share the import cache and build output. MUST NOT run a headless import or a game build in a checkout the editor has open. Use a separate worktree, or close the editor.

## Solutions and Builds

- Godot.NET.Sdk projects declare `Debug`, `ExportDebug` and `ExportRelease`, but no `Release`. A generated solution maps its `Release` rows to `Debug`, so write the solution's configuration sections by hand.
- MUST build the game project with warnings as errors, the same as the library. Godot's analyzers (`GD0001`…) report through the normal build.

## Imported Assets

- The glTF importer treats node-name suffixes as instructions (`-col`, `-colonly`, `-convcol`, `-noimp`, `-navmesh`, `-rigid`, `-occ`, `-vehicle`, `-wheel`; also with `_` or `$`, case-insensitive, after trailing digits are stripped). Generated asset names MUST avoid them unless the behaviour is wanted, or the import MUST turn suffixes off (`nodes/use_node_type_suffixes`).
- A headless import doesn't run editor-only steps (the texture "detect 3D" compression switch). When the editor and headless results differ, compare the `.import` settings.
