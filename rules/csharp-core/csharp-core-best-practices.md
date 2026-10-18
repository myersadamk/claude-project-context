---
paths:
  - "**/*.cs"
  - "**/*.csproj"
  - "**/Directory.Build.*"
  - "**/.editorconfig"
---

# C# Core — Best Practices

For plain .NET libraries with no engine or UI dependency. Engine-facing code adds its own stack rules.

## Project Setup

- MUST enable `<Nullable>enable</Nullable>` and `<WarningsAsErrors>nullable</WarningsAsErrors>` in the project, so every build (IDE, editor, CI) fails on a nullable warning, and MUST build with `-warnaserror` in the gate. Nullable analysis is compile-time only; it guarantees nothing unless warnings fail the build.
- MUST commit an `.editorconfig` and keep `dotnet format --verify-no-changes` clean. Formatting is the tool's job, not the reviewer's.
- MUST turn on analyzers by category, not wholesale. `<AnalysisLevelGlobalization>latest-recommended</AnalysisLevelGlobalization>` adds the culture rules (CA1304, CA1305, CA1309, CA1310, CA1311) with no noise; `latest-recommended` for everything adds dozens of style suggestions. Raise single rules in `.editorconfig` (`dotnet_diagnostic.CA1307.severity = warning`).
- MUST set `<EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>` and `<GenerateDocumentationFile>true</GenerateDocumentationFile>` with `CS1591` in `NoWarn`. Without the doc file, the compiler never checks `<see cref="…"/>` (CS1574) and unused usings (IDE0005) aren't reported in the build.
- Pin the SDK with `global.json`. The library's target framework is the API floor its consumers need; tests may target newer.
- MUST NOT reference engine or UI assemblies from the library. Enforce it with a test (-> csharp-core-testing.md).

## Naming and Layout

Follow the Microsoft C# conventions:

- `PascalCase` for types, methods, properties, events and constants. `camelCase` for locals and parameters. `_camelCase` for private fields. `I` prefix for interfaces.
- File-scoped namespaces, `using` directives outside the namespace, four-space indents, language keywords (`int`, not `Int32`).
- SHOULD keep one top-level type per file, named after the type (a StyleCop convention, SA1402, not a Microsoft one; engines that attach scripts by file name require it).
- `var` only when the type is obvious from the right-hand side.

## Types

- MUST make classes `sealed` unless they are designed for inheritance.
- MUST prefer immutable data for definitions and results: `record`, `readonly record struct`, `init` and `required` members, `IReadOnlyList<T>` in public signatures.
- MUST give identities their own type (`readonly record struct EntityId(int Value)`), not a bare `int` or `string`.
- MUST NOT keep mutable static state. State lives on instances that are passed in, so two simulations can run side by side and tests can run in parallel.
- Enum values that are stored, hashed or mixed into seeds MUST be explicit and never renumbered.

## Errors and Validation

- Validate at boundaries (content loading, public entry points). Internal code trusts its invariants.
- Content loaders SHOULD collect every error, each with its file and field, and report them together.
- Throw specific exceptions (`ArgumentOutOfRangeException`, `InvalidDataException`). MUST NOT catch `Exception` except at a top-level boundary that reports it.

## JSON (System.Text.Json)

- `required` means the property is present, not non-null, and nullable annotations aren't enforced at runtime. `"id": null` deserializes: null-check required references after loading, or set `RespectNullableAnnotations = true` (System.Text.Json 9+).
- MUST set `UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow` for hand-edited content, so a misspelled field is an error.
- Property names match case-sensitively by default, so `"Weight"` against `weight` is silently ignored unless unmapped members are disallowed.
- Duplicate keys are accepted by default, and the last one wins. Reject them for hand-edited content (`AllowDuplicateProperties = false`, or `JsonSerializerOptions.Strict`, System.Text.Json 10+). On older versions, know that a duplicate is silent.
- Enable comments and trailing commas explicitly (`ReadCommentHandling = JsonCommentHandling.Skip`, `AllowTrailingCommas = true`) if the format allows them, and test that it does.

## Hot Paths

- In per-tick or per-frame code: no LINQ, no lambdas that capture locals, no new reference-type allocations per iteration. Reuse lists with `Clear()`.
- `foreach` over a variable typed as an interface (`IEnumerable<T>`, `IReadOnlyList<T>`) boxes the enumerator. In hot loops, index with `for` or iterate the concrete `List<T>`.
- Expose long-lived views that are updated in place, rather than allocating snapshots every tick.
- Outside hot paths, write the clearest code and measure before optimizing.
