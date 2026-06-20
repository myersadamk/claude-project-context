---
paths:
  - "src/**/*.java"
---

# Spring Boot 3.5+ Patterns

Core patterns targeting Spring Boot 3.5+.

## Dependency Injection

### Constructor Injection Always
```java
@RequiredArgsConstructor
@Service
public class EntityService {
    private final EntityRepository repository;  // final = immutable
    private final ValidationService validator;
}

// NEVER field injection - untestable, hides dependencies
@Autowired private EntityRepository repository;
```

## Layering

### Controllers Are Thin Adapters
Business logic belongs in service classes:

```java
// GOOD: Controller delegates to service
@PostMapping("/process")
public ResponseEntity<Result> process(@Valid @RequestBody Request request) {
    var result = processingService.process(request);
    return ResponseEntity.ok(result);
}

// BAD: Controller orchestrates repositories directly
@PostMapping("/process")
public ResponseEntity<Result> process(@RequestBody Request request) {
    var entities = repository.findPending();
    var validated = validator.validate(entities);  // business logic leak
    // ... more orchestration that belongs in a service
}
```

## Transactions

### @Transactional on Service Layer
Transaction boundaries belong on services, not repositories:

```java
@Service
public class EntityService {

    @Transactional  // write transaction
    public void process(Entity entity) {
        repository.save(entity);
        auditService.record(entity);
    }

    @Transactional(readOnly = true)  // read-only for queries
    public List<Entity> findAll() {
        return repository.findAll();
    }
}
```

**Never on repositories** - they're called within service transactions.

## Configuration

### Type-Safe @ConfigurationProperties
```java
// GOOD: type-safe, validated
@ConfigurationProperties(prefix = "app.processing")
public record ProcessingConfig(
    @NotBlank String endpoint,
    @Min(1) @Max(100) int batchSize,
    Duration timeout,
    boolean enabled) { }

// BAD: scattered @Value annotations
@Value("${app.processing.endpoint}") String endpoint;
@Value("${app.processing.batch-size}") int batchSize;
```

### External Configuration Files
For large or domain-specific config, use `spring.config.import`:

```yaml
# application.yml
spring:
  config:
    import: classpath:processing-rules.yml

# processing-rules.yml
processing:
  rules:
    - name: validation
      enabled: true
```

### ObjectMapper Isolation
Never inject Spring's global ObjectMapper for file/export operations:

```java
// GOOD: local mapper scoped to use case
private static final ObjectMapper EXPORT_MAPPER = new ObjectMapper()
    .disable(SerializationFeature.INDENT_OUTPUT);

// BAD: global mapper may have unexpected config
@Autowired ObjectMapper objectMapper;
```

## Null Safety at Boundaries

### Validate at Public API Edges
```java
public Entity save(Entity entity) {
    Objects.requireNonNull(entity, "entity must not be null");
    Objects.requireNonNull(entity.name(), "entity.name must not be null");
    // internal methods can skip validation - fail fast at edges
    return repository.save(entity);
}
```

### Use Spring's @Nullable
```java
import org.springframework.lang.Nullable;

public record Entity(
    String name,
    @Nullable String description) { }
```

## Error Handling

### REST Controller Exception Handlers
```java
@ExceptionHandler(ConstraintViolationException.class)
public ResponseEntity<ErrorResponse> handleValidation(ConstraintViolationException ex) {
    return ResponseEntity.badRequest()
        .body(new ErrorResponse(ex.getMessage()));
}

@ExceptionHandler(EntityNotFoundException.class)
public ResponseEntity<ErrorResponse> handleNotFound(EntityNotFoundException ex) {
    return ResponseEntity.status(HttpStatus.NOT_FOUND)
        .body(new ErrorResponse(ex.getMessage()));
}
```

### Result Types for Expected Failures
Use the sealed-interface result type pattern (see java-jdk-21.md) for expected failures. Reserve exceptions for truly exceptional conditions.

```java
@PostMapping("/process")
public ResponseEntity<OperationResult> process(@RequestParam("file") MultipartFile file) {
    try {
        return ResponseEntity.ok(processingService.process(file));
    } catch (ProcessingException e) {
        log.error("Processing failed", keyValue("filename", file.getOriginalFilename()), e);
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
            .body(OperationResult.failure(e.getMessage()));
    }
}
```

## Security Patterns

### Identity from Security Context
Never trust client input for identity:

```java
// GOOD: identity from authenticated context
var userId = securityContext.getCurrentUserId()
    .orElseThrow(() -> new AccessDeniedException("Authentication required"));

// BAD: identity from request - trivially spoofable
@PostMapping("/action")
public void doAction(@RequestParam UUID userId) { ... }
```

### Method-Level Security
```java
@PostMapping("/admin/action")
@PreAuthorize("hasRole('ADMIN')")
public ResponseEntity<Result> adminAction() { ... }

@PostMapping("/user/action")
@PreAuthorize("isAuthenticated()")
public ResponseEntity<Result> userAction() { ... }
```

### Stateless Sessions
```java
http.sessionManagement(session ->
    session.sessionCreationPolicy(SessionCreationPolicy.STATELESS)
);
```
