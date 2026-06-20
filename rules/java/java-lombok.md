---
paths:
  - "src/**/*.java"
---

# Lombok Conventions

Lombok reduces verbosity, saving context and making diffs cleaner.

## Required Annotations

### @Slf4j on Services and Controllers
```java
@Slf4j
@Service
public class ProcessingService { }

@Slf4j
@Controller
public class ApiController { }
```

### @RequiredArgsConstructor for Dependency Injection
Always use with `final` fields:

```java
@Slf4j
@RequiredArgsConstructor
@Service
public class EntityService {
    private final EntityRepository repository;
    private final ValidationService validator;
    private final Clock clock;
}
```

**Never field injection:**
```java
// BAD: untestable, hides dependencies
@Autowired private EntityRepository repository;
```

### @Builder on Records Only
Use `@Builder` exclusively on records, never on classes:

```java
@Builder
public record Entity(
        String name,
        Status status,
        @Nullable String description) {

    public Entity {
        if (description == null) description = "";
    }
}
```

**When to use @Builder:**
- Domain models with multiple fields
- DTOs and API response objects
- Configuration records
- Any record where construction benefits from named parameters

## Annotations to Avoid (Production Code)

| Annotation | Problem | Alternative |
|------------|---------|-------------|
| `@Data` | Mutable, generates setters | Use records |
| `@Value` | Superseded | Use records |
| `@AllArgsConstructor` | Brittle to field order changes | Use @RequiredArgsConstructor or @Builder |
| `@Getter/@Setter` | Encourages mutability | Use records or explicit methods |
| `@ToString/@EqualsAndHashCode` | Records provide these | Use records |

These annotations are acceptable in **test helper classes only**.
