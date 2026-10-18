---
paths:
  - "**/*.cs"
---

# C# Core — Testing

## Known Answers Over Self-Consistency

- Every function whose output is fixed by a spec or a seed MUST have a known-answer test. Its expected values come from an independent reference (a short script in another language, or a hand derivation), never from printing what the code under test returns.
- Range, round-trip and "same seed twice" tests are supplements. They can't tell a correct sequence from a different deterministic one.
- MUST NOT compute a test's expectation with the function under test. A wrong transform that both writes and reads a value cancels out and passes.
- Watch for properties that hold by construction: a per-step displacement that telescopes to the total proves nothing about the curve. Pin individual steps instead.
- Deterministic doubles MUST be compared exactly, with a failure message that prints every digit (`"R"` format). A tolerance hides "always one tick behind".

## Tests With Teeth

- After adding tests for a rule, break the rule on purpose (one small mutation at a time) and confirm a test fails. Restore the file byte for byte afterwards.
- Classify each catch. Caught by an assertion is real coverage. Caught only by an exception (a guard in another module, a duplicate-key throw) is borrowed: try a quieter mutant that avoids the throw.

## Structure

- Algorithm tests MUST read frozen fixture copies, not live content, so content edits never break algorithm tests. One separate test loads and validates every live content file.
- MUST NOT share mutable static state between tests. xUnit runs test classes in parallel by default.
- Use `[Theory]` with `[InlineData]` or `[MemberData]` for tables of known answers.
- To see state in a failing test, take `ITestOutputHelper` in the constructor and run with `--logger "console;verbosity=detailed"`. MUST NOT throw temporary exceptions or leave debug prints.
- Name tests for the behaviour they pin: `Unobstructed_dodge_travels_the_tuned_distance`, not `Test3`.
- A test project may target a newer framework than the library. Runtime behaviour (JSON parsing, globalization) then comes from the test's runtime, not the library's target.

## Time Is an Input

- MUST NOT assert on wall-clock durations in functional tests ("finished within 1 s"). A loaded machine fails them: parallel builds, renders and agents are normal here.
- Code that needs the time MUST take it as an input. In .NET 8+ use `System.TimeProvider` (inject it; production passes `TimeProvider.System`) and test with `FakeTimeProvider` (`Microsoft.Extensions.TimeProvider.Testing`), advancing time explicitly. Simulation code already uses ticks, not clocks.
- Anything that polls (file watchers, hot reload, retries) MUST expose the poll step, so a test calls it directly and asserts "on the next poll" or "within N polls", not "within N seconds".
- Wall-clock timeouts exist only as **hang guards**: generous (about 10× the expected time), and they fail with "hung", never as a correctness check.
- Speed is measured, not asserted, in the gate: performance belongs in perf tests (e.g. `Category=Perf`) that report numbers and run separately.

## Architecture Tests

- Enforce layer boundaries with a test, not a grep: check `typeof(SomeCoreType).Assembly.GetReferencedAssemblies()` for forbidden names. A grep over the source tree also matches build output, comments and paths.
- A cheap source scan ("this module never names X") is fine for vocabulary rules. Skip comment lines, and accept that substring matches are crude.
