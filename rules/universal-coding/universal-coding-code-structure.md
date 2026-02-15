# Code Structure & Readability

## Function Length

- **Soft limit: ~50 lines.** If a function exceeds this, look for extraction opportunities.
- **Hard ceiling: 100 lines.** Functions past this MUST be split. Length is a symptom — the real problem is usually multiple responsibilities or duplicated patterns.
- Count logic lines, not blank lines or closing braces.

## Single Responsibility

Each function does one thing at one level of abstraction.

- If you can describe a block with a comment like "Step 3: clean stale entries", that block is a candidate for its own function.
- If the same pattern appears twice with minor variations, extract it. Don't wait for a third occurrence.
- A function that creates, validates, transforms, AND persists is doing too much.

## Composition Over Long Blocks

Prefer a high-level function that reads like an outline:

```
install():
    prepare_directories()
    sync_rules()
    sync_skills()
    write_manifest()
```

Each step is a focused function. The parent function shows intent; the children show implementation.

## Nesting Depth

- **Maximum 3 levels of indentation** inside a function body (not counting the function definition itself).
- Use early returns, `continue`, and guard clauses to flatten logic.
- Deeply nested code is a signal to extract a helper.

```
// Bad — 4 levels deep
process(items):
    for item in items:
        if item.isValid:
            if item.needsUpdate:
                if not item.isLocked:
                    update(item)

// Good — guard clauses flatten it
process(items):
    for item in items:
        if not item.isValid → continue
        if not item.needsUpdate → continue
        if item.isLocked → continue
        update(item)
```

## Early Returns

Return early for preconditions and error cases. Don't wrap the entire function body in an `if`.

```
// Bad — nested conditionals
getUser(id):
    if id is not null:
        user = lookup(id)
        if user is not null:
            return user
    return null

// Good — early return
getUser(id):
    if id is null → return null
    return lookup(id)
```

## Naming

- Names describe **what**, not **how**: `activeUsers` not `filteredList`
- Boolean names state the condition: `isStale`, `hasManifest`, `shouldClean`
- Function names are verbs: `resolveSkill`, `discoverRules`, `cleanStaleLinks`
- Avoid generic names: `data`, `result`, `items`, `tmp`, `val` — unless the scope is 3 lines or fewer
- No abbreviations in public APIs: `configuration` not `cfg`, `manifest` not `mfst`

## Consistent Abstraction Level

Within a single function, all statements should operate at the same level of detail. Don't mix high-level orchestration with low-level implementation.

```
// Bad — mixed levels
deploy():
    validateConfig()
    socket.connect(host, port)   // low-level detail
    sendBytes(payload)           // low-level detail
    notifyTeam()

// Good — consistent level
deploy():
    validateConfig()
    uploadArtifact()
    notifyTeam()
```

## Anti-Patterns

| Pattern | Problem | Fix |
| --- | --- | --- |
| God function (100+ lines) | Untestable, hard to read | Extract focused helpers |
| Duplicated blocks with minor variations | Bugs fixed in one copy but not the other | Extract parameterized function |
| Deep nesting (4+ levels) | Cognitive load, hidden paths | Guard clauses, early returns, extract |
| Comment-separated sections | The comments are naming functions for you | Extract into named functions |
| Generic variable names | Ambiguous at point of use | Name describes the content |
| Mixed abstraction levels | Reader jumps between thinking modes | Keep each function at one level |
