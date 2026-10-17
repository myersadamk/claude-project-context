# C# Core — Review Checklist

## Verification Commands

All MUST pass before approval:

```bash
dotnet build -warnaserror && dotnet test --no-build && dotnet format --verify-no-changes
```

If the project wraps these in a gate script (named in its CLAUDE.md), run that instead and read its summary line.

### Fixing formatting failures

If `dotnet format --verify-no-changes` fails, run `dotnet format`, review the diff, and commit the formatting separately from logic changes.

## Checklist

### Project (-> csharp-core-best-practices.md)

- [ ] Builds with zero warnings; nullable enabled
- [ ] No engine or UI reference from the library; the architecture test passes
- [ ] No new package without justification

### Determinism (-> csharp-core-determinism.md)

- [ ] Randomness comes from a passed-in seeded stream; no `System.Random`, clock, `Guid` or `GetHashCode` in output
- [ ] No `Math.Sin/Cos/Pow/Atan2/Exp/Log`, FMA or SIMD in deterministic state
- [ ] No dictionary or set order reaches output; sorts are total or stable; strings compared ordinally
- [ ] Numbers parsed and formatted with the invariant culture
- [ ] Time is integer ticks; NaN and out-of-range values rejected at load

### Types and Errors (-> csharp-core-best-practices.md)

- [ ] Classes sealed; definitions immutable; ids have their own types
- [ ] No mutable static state
- [ ] JSON: unknown members disallowed, required references null-checked

### Tests (-> csharp-core-testing.md)

- [ ] Known answers from an independent reference for every value-producing function changed
- [ ] Exact comparison for deterministic doubles
- [ ] At least one mutation of the new logic was caught by an assertion
