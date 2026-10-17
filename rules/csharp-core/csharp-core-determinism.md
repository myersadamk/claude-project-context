---
paths:
  - "**/*.cs"
---

# C# Core — Determinism

For code whose output must be reproducible from a seed and inputs: simulation, procedural generation, loot and stat calculation. Same seed, same inputs, same bits, on every run, machine and OS. Presentation code (rendering, audio, UI) is exempt, but MUST NOT feed values back into deterministic state.

## Randomness

- MUST take randomness from an explicit seeded generator that is passed in. MUST NOT use `System.Random`, `Random.Shared`, `Guid.NewGuid()`, `DateTime.Now`/`UtcNow`, `Stopwatch` or `Environment.TickCount` for anything that affects output.
- MUST implement the generator from a published algorithm (SplitMix64, PCG, xoshiro) and pin every public draw method with known-answer tests. `System.Random`'s sequence for a given seed isn't promised across .NET versions.
- MUST keep separate streams per concern (map, spawns, loot, combat), each derived from the run seed with a fixed mix, so a new draw in one doesn't reshuffle the others. Stream ids are explicit enum values that are never renumbered.
- The order of draws is part of the contract. Changing it is a breaking change: update the spec, the reference and the known answers together.

## Floating Point

- `+ - * /` and `Math.Sqrt` are correctly rounded by IEEE 754 and give the same bits on every .NET platform. `Math.Sin/Cos/Tan/Asin/Acos/Atan/Atan2/Pow/Exp/Log/Cbrt` and all of `MathF` call the platform's C runtime, and they differ between Windows and Linux even on the same .NET runtime. MUST NOT use them in deterministic state. Prefer trig-free formulations (rotate by a known cos/sin pair), or a specified implementation pinned by known answers.
- MUST keep deterministic state in one precision (`double`). Convert to `float` only at the presentation boundary.
- MUST NOT use `Math.FusedMultiplyAdd`, `System.Numerics.Vector*` or hardware intrinsics in deterministic math: they round differently from the scalar code and the reference.
- MUST evaluate expressions in the order the spec writes them. `a * (b / c)` and `(a * b) / c` are different numbers, so an algebraic "simplification" is a behaviour change.
- MUST sum and multiply collections in a canonical order (sorted values, or ascending id). Float addition isn't associative.
- MUST state the rounding mode: `Math.Round(x, MidpointRounding.AwayFromZero)`. The default rounds half to even.
- MUST reject NaN and infinity at load time. Every comparison with NaN is false, so guards pass silently.
- MUST range-check a `double` before casting it to an integer. The C# spec leaves NaN and out-of-range results unspecified; .NET 9+ saturates on x64 while older runtimes don't, and the runtime the code runs on decides, not its target framework.

## Iteration Order

- MUST NOT let `Dictionary` or `HashSet` enumeration order reach output, events, sums or random draws. The order is undefined: in practice it's insertion order until a `Remove` frees a slot that a later `Add` reuses. Iterate sorted keys, a list kept in id order, or a `SortedDictionary`.
- `List<T>.Sort` and `Array.Sort` are unstable. Sort by a total order (tie-break on id), or use LINQ `OrderBy`, which is stable.
- MUST compare strings ordinally for sorting and lookups (`StringComparer.Ordinal`). The default string sort is culture-sensitive, and no analyzer flags `List<string>.Sort()` without a comparer.
- MUST sort `Directory.GetFiles`/`EnumerateFiles` results ordinally before use. Filesystem order varies by OS.

## Hashes, Culture and Time

- MUST NOT store, compare across runs, or pick content with `string.GetHashCode()` or `HashCode.Combine`: they're randomized per process. Use a specified hash (FNV-1a, or xxHash with a fixed seed).
- MUST parse and format numbers with `CultureInfo.InvariantCulture`. That includes interpolation (`string.Create(CultureInfo.InvariantCulture, $"…")` or `FormattableString.Invariant`), concatenation and `StringBuilder.Append(double)`, which analyzers don't flag. Some cultures write `1,5`; Swedish writes `−1,5` with a Unicode minus (U+2212).
- Simulation time MUST be an integer tick count. Convert seconds to ticks once, at load, with validation. MUST NOT accumulate frame deltas into deterministic state.

## Proof

- MUST have a test that runs the same seed and inputs twice and compares a full-state hash, plus known-answer tests from an independent reference (-> csharp-core-testing.md).
- SHOULD enforce the banned APIs with `Microsoft.CodeAnalysis.BannedApiAnalyzers` (RS0030) and a `BannedSymbols.txt` on the deterministic project, rather than relying on review. List every overload (`M:System.Math.Pow(System.Double,System.Double)`): a bare method name bans nothing. Indirect uses (`HashCode.Combine` of a string) still need review.
