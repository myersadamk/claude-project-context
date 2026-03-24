# Java Spring — Review Checklist

## Verification Commands

All MUST pass before approval:

```bash
./gradlew test
```

## Checklist

### Java Quality (-> java-jdk-21.md)

- [ ] Records for value objects, not classes with getters/setters
- [ ] Functional Optional chaining (no `.get()`, no null returns)
- [ ] `var` used where type is obvious from RHS
- [ ] No wildcard imports
- [ ] Text blocks for multi-line strings
- [ ] `.formatted()` over `String.format()`

### Lombok (-> java-lombok.md)

- [ ] `@RequiredArgsConstructor` with `final` fields for DI (no field injection)
- [ ] `@Builder` on records only
- [ ] No `@Data`, `@Value`, `@AllArgsConstructor` in production code

### Spring Boot (-> java-spring-boot.md)

- [ ] Controllers are thin adapters — business logic in services
- [ ] `@Transactional` on service layer (read-only for queries), never on repositories
- [ ] `@ConfigurationProperties` records for configuration (no scattered `@Value`)
- [ ] Identity from security context, never from client input
- [ ] Result types for expected failures, exceptions for exceptional conditions

### Testing (-> java-spring-testing.md)

- [ ] Narrowest test slice used (`@WebMvcTest`, `@DataJpaTest`, `@SpringBootTest`)
- [ ] Meta-annotations for common test configurations
- [ ] Transactional tests for automatic rollback (no manual cleanup)
- [ ] `@MockBean` for Spring context tests, `@Mock` for unit tests
- [ ] Clock injection for time-dependent code
