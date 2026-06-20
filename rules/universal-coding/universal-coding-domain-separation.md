# Domain Separation — Data vs. Behavior

## The Principle

Domain objects MUST be separable into **what something is** (data) and
**what something does** (behavior). When a single type carries both
identity/metadata and executable logic, it becomes harder to serialize,
test, compose, and reason about at the catalog level.

This is not "no methods on objects." It's a structural rule: **the type
that travels through the system should be pure data.** Behavior that
operates on that data lives in a registry, service, or function layer
that accepts the data type as input.

## When This Matters

- A type is stored, persisted, or serialized
- A type appears in configuration or user-facing selection
- Multiple subsystems need to reason about the type differently
  (UI needs display info, engine needs generation logic, filtering needs
  constraints)
- You need to enumerate, filter, or transform a catalog of instances
  without importing their behavior

## The Split

| Layer | Contains | Example |
| --- | --- | --- |
| **Data type** | Identity, display metadata, structural properties, constraints | `PatternTemplate { id, displayName, conceptGroup, beatCost, constraints }` |
| **Behavior registry** | Functions keyed by ID, execution context, runtime dependencies | `GENERATION_REGISTRY: Map<PatternId, GenerationEntry>` |

The data type is the **lingua franca** — every subsystem can import and
operate on it. The behavior registry is imported only by the subsystem
that executes behavior.

## Rules

### Data types MUST be pure

- MUST NOT contain functions, closures, or methods with side effects
- MUST be serializable to JSON without loss (no `Map`, `Set`, functions)
- MUST carry enough information for display, filtering, and selection
  without importing behavior
- MAY contain derived constants (`beatCost`) that describe structure

### Behavior MUST be keyed to data

- Behavior registries MUST use the data type's identity key (ID, enum
  value) as the lookup key
- MUST NOT use the data object itself as a key — use its ID
- A missing registry entry is a hard error, not a silent fallback

### Subsystems MUST import only what they need

- UI/config layers import the **data type** — never the behavior registry
- Execution layers import **both** — data for identity, registry for logic
- Filtering/catalog layers import **data only** — they reason about
  structure, not execution

### The data catalog MUST be the single source of truth

- Enumeration, filtering, grouping, and display MUST derive from the data
  catalog
- MUST NOT maintain a parallel list in the behavior registry
- The behavior registry is keyed by ID — the catalog defines which IDs
  exist

## How to Recognize a Violation

| Smell | Problem | Fix |
| --- | --- | --- |
| Type has both `displayName` and `execute()` | Data and behavior coupled | Split into data type + behavior registry |
| Filtering logic imports execution functions | Catalog layer pulls in runtime deps | Filter on data properties only |
| Serializing requires stripping functions | Type isn't naturally serializable | Move functions to registry |
| Adding a new consumer requires importing unrelated logic | Coupling through the god-type | Split so consumers import only what they need |
| Test needs to mock a method on a data object | Behavior is embedded in data | Extract behavior, test it separately |
| "I need to call `.generate()` just to check if this fits" | Execution used for structural questions | Add structural properties (`beatCost`) to data |

## Applying to New Domains

When defining a domain object, ask:

1. **Can I enumerate all instances without importing any functions?**
   If not, the type carries behavior it shouldn't.
2. **Can I serialize an instance to JSON and reconstruct it?**
   If not, there are non-data fields.
3. **Does the UI need to import the execution engine just to display a
   list?** If so, the type is too fat.
4. **Can I write a filtering/selection system that never calls a method
   on the instances?** If not, structural properties are missing.

If any answer is "no," split the type.

## Exceptions

- **Tiny, self-contained value objects** (e.g., `NoteRange` with a
  `.contains(note)` method) are fine as unified types — the behavior is
  trivially derived from the data and has no external dependencies.
- **Builder patterns** that accumulate configuration before producing a
  final data object are fine — the builder is not the domain type.
- When behavior has **zero external dependencies** and is **derivable
  purely from the object's own fields**, colocating it is acceptable.
  The threshold: if you can implement it as a pure function of `this`
  with no imports, it may stay. If it needs a registry, context, or
  external state, it MUST be extracted.
