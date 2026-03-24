---
name: domain-separation-review
description: Use after defining or significantly modifying domain types to detect god-types and propose data/behavior splits. Traces how types are consumed across the codebase.
argument-hint: "[type-name | file-path | 'all']"
user-invocable: true
disable-model-invocation: false
---

# Domain Separation Review

Structural review that traces how domain types flow through the codebase,
identifies coupling between data and behavior, and proposes concrete splits.

## Why This Exists

Static rules can say "don't put functions on data types." But god-types
don't start as god-types — they start as clean, collocated interfaces and
grow fields as new consumers appear. The coupling only becomes visible when
you map the **consumption graph**: who imports this type, and which fields
do they actually use?

This review does that mapping. It's a checkpoint, not a linter.

## When to Invoke

- After defining a new domain type that will be used by 2+ subsystems
- Before a major PR that introduces or modifies core types
- When you notice a type accreting fields from different concerns
- When a subsystem needs to import something heavy just to use a type
- Periodically on core domain types (monthly or per-milestone)

## Process

### 1. Identify Target Types

Parse `$ARGUMENTS`:

- **Type name** (e.g., `PatternTemplate`): search for the type definition
- **File path** (e.g., `src/lib/core/domain.ts`): analyze all exported
  types from that file
- **`all`**: scan the domain layer for types exported from core modules
  (heuristic: files in paths matching `*/core/*`, `*/domain/*`,
  `*/models/*`, `*/types/*`, or files that are imported by 5+ other files)
- **No argument**: analyze types changed in the current diff
  (`git diff --cached` + `git diff`, extract type definitions from
  changed hunks)

For each target type, proceed through steps 2-5.

### 2. Map the Type's Shape

Read the type definition. Classify each field:

| Category | Description | Examples |
|----------|-------------|---------|
| **Identity** | Unique key, name, slug | `id`, `slug`, `key` |
| **Display** | Human-readable metadata | `displayName`, `description`, `icon` |
| **Structural** | Properties that describe what this thing *is* | `beatCost`, `conceptGroup`, `status`, `constraints` |
| **Behavioral** | Functions, methods, closures | `generate()`, `validate()`, `transform()` |
| **Context** | Runtime dependencies, external references | `startRange`, `harmonicContext`, `config` |

Report the breakdown:

```
## PatternTemplate — Field Analysis

Identity:     id (PatternId)
Display:      displayName, description
Structural:   conceptGroup, beatCost, constraints
Behavioral:   generate, generateExample          ← separation candidates
Context:      startRange, harmonicContext         ← separation candidates

Shape: 9 fields (4 data, 3 behavioral/context)
```

**Behavioral and Context fields are separation candidates** — they indicate
the type is carrying execution concerns.

### 3. Trace the Consumption Graph

For each target type, find every file that imports it. For each consumer:

1. Which fields does the consumer actually access?
2. What subsystem does the consumer belong to?
   (UI, configuration, generation/execution, persistence, testing)
3. Does the consumer need to import other modules *because* of this type?
   (e.g., importing a generation engine just to access a method on the type)

Build a consumption matrix:

```
## PatternTemplate — Consumption Graph

Consumer                          | Subsystem     | Fields Used
----------------------------------|---------------|---------------------------
PatternSection.tsx                | UI            | id, displayName, conceptGroup
PatternTile.tsx                   | UI            | id, displayName, generate ← pulls in engine
drill-config-store.ts             | Config        | id, category
computeVariantsForTimeSignature   | Filtering     | id, displayName, beatCost, constraints
VoiceGenerator                    | Execution     | id, generate, startRange, harmonicContext
measure-fill.ts                   | Execution     | generate (via pattern)
variant-system.test.ts            | Testing       | id, displayName, beatCost, conceptGroup

Cross-subsystem behavioral access:
  PatternTile.tsx (UI) imports generate → UI depends on execution logic
```

### 4. Diagnose

Apply the diagnostic questions from `universal-coding-domain-separation.md`:

**Question 1: Can I enumerate all instances without importing functions?**
Check if there's a way to list/filter/iterate instances using only data
fields. If any enumeration code imports behavioral fields, flag it.

**Question 2: Can I serialize an instance to JSON and reconstruct it?**
Check if the type contains non-serializable fields (functions, Maps, Sets,
class instances with methods). If so, flag which fields block
serialization.

**Question 3: Does the UI import execution logic just to display a list?**
Check if UI components import behavioral fields or modules that exist
solely to support behavioral fields.

**Question 4: Can filtering/selection work without calling methods?**
Check if any filtering logic calls methods on instances instead of
reading structural properties.

Report each diagnosis:

```
## PatternTemplate — Diagnosis

1. Enumeration without functions?     NO — patternRegistry iteration
   includes generate/generateExample
2. Serializable to JSON?              NO — generate and generateExample
   are function references
3. UI imports execution logic?        YES — PatternTile imports generate
   for preview rendering
4. Filtering without method calls?    PARTIAL — patternFitsTimeSignature
   calls generateExample to check length
                                       (should be a structural property)

Severity: HIGH — 3 of 4 diagnostic questions indicate coupling
```

### 5. Propose Split

If 2+ diagnostic questions indicate coupling, propose a concrete split:

```
## PatternTemplate — Proposed Split

### Data Type (stays as PatternTemplate)
  id: PatternId
  displayName: string
  description: string
  conceptGroup: ConceptGroup
  beatCost: number                    ← NEW: replaces runtime length check
  constraints?: PatternConstraints

### Behavior Registry (new: GenerationRegistry)
  Key: PatternId
  Entry: {
    generate: GenerateFn
    generateExample: GenerateExampleFn
    startRange: NoteRange
    harmonicContext: HarmonicContextRequirement
  }

### Migration Impact
  - PatternSection.tsx: no change (already uses data fields only)
  - PatternTile.tsx: import getGenerationEntry() instead of pattern.generate
  - VoiceGenerator: import both PatternTemplate + getGenerationEntry()
  - computeVariantsForTimeSignature: no change (uses beatCost, not generate)
  - 6 test files need updating

### New Structural Properties
  beatCost was previously implicit (derived by calling generateExample
  and counting notes). Making it explicit means filtering no longer
  needs the generation engine.
```

If 0-1 diagnostic questions indicate coupling, report the type as healthy:

```
## NoteRange — Diagnosis

All 4 diagnostic questions pass. contains() is a pure function of own
fields with zero imports. No split needed.
```

## Output Format

```
# Domain Separation Review

## Summary
  Types analyzed: 3
  Healthy: 1
  Splits proposed: 2

## PatternTemplate
  [field analysis]
  [consumption graph]
  [diagnosis]
  [proposed split]

## Exercise
  [field analysis]
  [consumption graph]
  [diagnosis]
  [proposed split]

## NoteRange
  [field analysis]
  [diagnosis: healthy]
```

## Dispatching as a Subagent

When dispatching this review as a subagent (e.g., from a development
workflow), use the Explore agent type with a prompt based on this
template:

```
Perform a domain separation review on [TYPE_NAME] defined in [FILE_PATH].

1. Read the type definition
2. Search for all files that import this type (use Grep for the type name)
3. For each importing file, identify which fields are accessed
4. Apply the 4 diagnostic questions from the domain separation principle
5. If 2+ questions indicate coupling, propose a concrete split with
   migration impact

Report findings in the structured format from the domain-separation-review
skill.
```

## What This Is Not

- Not a general code review — use `superpowers:requesting-code-review`
- Not a style/lint check — use `cpc-audit`
- Not an architecture design session — use `superpowers:brainstorming`

This is specifically a **structural coupling analysis** for domain types.
