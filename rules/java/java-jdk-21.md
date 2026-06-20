---
paths:
  - "src/**/*.java"
---

# Java 21+ Idioms

Modern Java idioms targeting JDK 21+.

## Expressions Over Statements

### Lambdas Over Anonymous Classes
```java
// GOOD
executor.submit(() -> process(item));

// BAD
executor.submit(new Runnable() {
    @Override public void run() { process(item); }
});
```

### Streams Over Manual Iteration
Prefer streams and collectors, except when iteration improves clarity:

```java
// GOOD: declarative
var names = users.stream()
    .filter(User::isActive)
    .map(User::name)
    .toList();

// BAD: imperative
var names = new ArrayList<String>();
for (var user : users) {
    if (user.isActive()) {
        names.add(user.name());
    }
}
```

## Type Inference

### Use `var` Where It Improves Readability
```java
// GOOD: type is obvious from RHS
var users = userRepository.findAll();
var config = new ProcessingConfig();

// BAD: var obscures important type info
var result = process(input);  // what type is result?

// GOOD: explicit when type matters
Optional<User> result = process(input);
```

### Avoid `final` Clutter
Skip `final` except when it aids readability (e.g., when re-assigning some variables but not others).

## Optionals

### Functional Style Over Imperative
```java
// GOOD: functional chaining
return findNearest(query)
    .map(match -> evaluate(match, context))
    .orElseGet(() -> defaultResult());

// BAD: imperative with isEmpty/get
var result = findNearest(query);
if (result.isEmpty()) {
    return defaultResult();
}
return evaluate(result.get(), context);  // get() is a code smell
```

Chain operations: `.map()`, `.filter()`, `.flatMap()`, `.or()`, `.orElseGet()`

### Never Return Null
Return `Optional` for values that may be absent. Reserve `null` for "not yet initialized" internal state.

## Records

### Use Records for Value Objects
```java
@Builder
public record ProcessingResult(
        UUID entityId,
        Status status,
        @Nullable String errorDetail) {

    // Compact constructor for defaults
    public ProcessingResult {
        if (errorDetail == null) errorDetail = "";
    }
}
```

Records provide: immutability, equals/hashCode, toString, accessors.

## String Formatting

### Use `.formatted()` Over `String.format()`
```java
// GOOD: instance method, reads left-to-right
var msg = "Processing %s with threshold %.3f".formatted(name, threshold);

// BAD: static method, harder to read
var msg = String.format("Processing %s with threshold %.3f", name, threshold);

// BAD: concatenation
var msg = "Processing " + name + " with threshold " + threshold;
```

### Text Blocks for Multi-line Strings
```java
// GOOD: text block
var sql = """
    SELECT id, name
    FROM entity
    WHERE status = ?
    ORDER BY created_at
    """;

// BAD: concatenation
var sql = "SELECT id, name "
    + "FROM entity "
    + "WHERE status = ? "
    + "ORDER BY created_at";
```

## Imports

### Never Use Wildcard Imports
```java
// GOOD
import static org.mockito.Mockito.when;
import static org.mockito.Mockito.verify;

// BAD
import static org.mockito.Mockito.*;
```

### Avoid Qualified Inline References
Use imports, not inline qualification (except for naming collisions):

```java
// GOOD
import java.util.Map;
Map<String, String> data = ...

// BAD
java.util.Map<String, String> data = ...
```

## Type Safety

### Avoid Casting from Generic Types
Never cast from `Map<String, Object>` or similar. Use type-safe binding:

```java
// GOOD: type-safe configuration
public record Config(String value, List<String> items) { }

// BAD: runtime casting
Map<String, Object> raw = yaml.load(stream);
String value = (String) raw.get("key");  // runtime error if wrong type
```
