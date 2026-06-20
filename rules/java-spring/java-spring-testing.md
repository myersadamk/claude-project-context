---
paths:
  - "src/test/**/*.java"
---

# Spring Testing Patterns

Spring-specific testing conventions building on general testing principles.

## Test Slicing

Use the narrowest slice that tests your behavior:

| Annotation | Use Case | What's Loaded |
|------------|----------|---------------|
| `@WebMvcTest` | Controller tests | Web layer only |
| `@DataJpaTest` | Repository tests | JPA + database |
| `@SpringBootTest` | Integration tests | Full context |

```java
// Controller slice - fast, focused
@WebMvcTest(EntityController.class)
class EntityControllerTest {
    @Autowired MockMvc mockMvc;
    @MockBean EntityService entityService;
}

// Repository slice - real database
@DataJpaTest
@Import(EntityRepository.class)
class EntityRepositoryTest {
    @Autowired EntityRepository repository;
}

// Full integration - use sparingly
@SpringBootTest
class EntityIntegrationTest { }
```

## Test Annotations

Create meta-annotations to bundle common test slice configurations. This reduces annotation soup and enforces consistency across test classes.

```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@SpringBootTest
@Transactional
@ActiveProfiles("test")
public @interface IntegrationTest { }

// Usage
@IntegrationTest
class MyIntegrationTest { }
```

## Transactional Tests

Tests should be transactional for automatic rollback:

```java
@DataJpaTest  // includes @Transactional
class RepositoryTest {
    @Test
    void shouldSaveEntity() {
        repository.save(testEntity);
        // Automatically rolled back after test
    }
}
```

**Never manually delete test data** - rely on transaction rollback.

## MockBean vs Mock

| Approach | When to Use |
|----------|-------------|
| `@MockBean` | Replace a Spring bean in the context |
| `@Mock` + `@InjectMocks` | Unit tests without Spring context |

```java
// Spring context test - use @MockBean
@WebMvcTest(EntityController.class)
class ControllerTest {
    @MockBean EntityService entityService;
}

// Unit test - use @Mock
@ExtendWith(MockitoExtension.class)
class ServiceTest {
    @Mock EntityRepository repository;
    @InjectMocks EntityService service;
}
```

## TestContainers

For integration tests requiring real infrastructure:

```java
@Testcontainers
@SpringBootTest
class DatabaseIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16")
        .withDatabaseName("test");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }
}
```

## Clock Injection for Time

Inject `Clock` for testable time-dependent code:

```java
// Production config
@Bean
Clock clock() {
    return Clock.systemUTC();
}

// Test config
@TestConfiguration
class TestConfig {
    @Bean
    Clock clock() {
        return Clock.fixed(Instant.parse("2024-01-15T10:00:00Z"), ZoneOffset.UTC);
    }
}
```

## REST API Testing

```java
@WebMvcTest(EntityController.class)
class EntityControllerTest {

    @Autowired MockMvc mockMvc;
    @MockBean EntityService entityService;

    @Test
    void shouldReturnEntity() throws Exception {
        when(entityService.findById(any())).thenReturn(Optional.of(testEntity));

        mockMvc.perform(get("/api/entities/{id}", entityId))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.name").value("Test Entity"));
    }

    @Test
    void shouldReturn404WhenNotFound() throws Exception {
        when(entityService.findById(any())).thenReturn(Optional.empty());

        mockMvc.perform(get("/api/entities/{id}", entityId))
            .andExpect(status().isNotFound());
    }
}
```
