---
paths:
  - "src/**/graphql/**/*.java"
  - "src/main/resources/graphql/**"
---

# Spring GraphQL Patterns

Patterns for Spring GraphQL with DataLoader integration.

## Controller Structure

### Query Controllers
```java
@Slf4j
@Controller
public class EntityQueryController {

    @QueryMapping
    public CompletableFuture<EntityModel> entity(
            @Argument String id,
            DataFetchingEnvironment env) {
        UUID entityId = UUID.fromString(id);
        DataLoader<UUID, EntityModel> loader = env.getDataLoader(EntityBatchLoader.REGISTRY_KEY);
        return loader.load(entityId);
    }

    @SchemaMapping(typeName = "Entity", field = "related")
    public CompletableFuture<List<RelatedModel>> related(
            EntityModel entity,
            DataFetchingEnvironment env) {
        DataLoader<UUID, List<RelatedModel>> loader = env.getDataLoader(REGISTRY_KEY);
        return loader.load(entity.id())
            .thenApply(result -> result != null ? result : List.of());
    }
}
```

### Mutation Controllers
```java
@MutationMapping
@PreAuthorize("isAuthenticated()")
public ResultModel mutate(@Argument InputModel input) {
    var user = currentUserProvider.getCurrentUser()
        .orElseThrow(() -> new AccessDeniedException("Authentication required"));
    return service.process(input, user);
}
```

## DataLoader Pattern

### Contract: All Keys Must Exist in Result
```java
public Publisher<Map<UUID, EntityModel>> load(Set<UUID> ids, BatchLoaderEnvironment env) {
    return Mono.fromCallable(() -> service.findByIds(List.copyOf(ids)))
        .map(entities -> {
            Map<UUID, EntityModel> models = entities.stream()
                .filter(Objects::nonNull)
                .collect(Collectors.toMap(Entity::id, EntityModel::fromEntity));

            // CRITICAL: Pad all requested keys - DataLoader contract requirement
            ids.forEach(id -> models.putIfAbsent(id, null));
            return models;
        });
}
```

### RegisterableLoader Interface

Define a common interface for DataLoader registration so loaders are self-describing and centrally discovered via Spring's dependency injection.

```java
public interface RegisterableLoader<K, V> {
    String REGISTRY_KEY = "...";
    Publisher<Map<K, V>> load(Set<K> keys, BatchLoaderEnvironment env);
    void register(BatchLoaderRegistry registry);
}
```

### Centralized Registration

Centralize loader registration in a single config class rather than scattering registration across controllers. Use `@PostConstruct` to auto-register all loaders found via DI.

```java
@Configuration
public class DataLoaderConfiguration {
    private final BatchLoaderRegistry registry;
    private final List<RegisterableLoader<?, ?>> loaders;

    @PostConstruct
    void registerAll() {
        loaders.forEach(loader -> loader.register(registry));
    }
}
```

## Type Safety with Generics

Preserve type parameters at boundaries:

```java
// In controllers - explicit type capture
DataLoader<UUID, EntityModel> loader = env.getDataLoader(EntityBatchLoader.REGISTRY_KEY);

// In tests - typed mocks
@Mock DataLoader<UUID, EntityModel> loaderMock;

// When stubbing erased return types
when(env.<UUID, EntityModel>getDataLoader(REGISTRY_KEY))
    .thenReturn(loaderMock);
```

## Error Handling

### Centralized Exception Resolver
```java
@Override
protected GraphQLError resolveToSingleError(Throwable ex, DataFetchingEnvironment env) {
    // Log full details internally
    log.error("GraphQL error",
        keyValue("operation", env.getOperationDefinition().getName()),
        keyValue("field", env.getField().getName()),
        ex);

    // Return safe message to client
    return switch (ex) {
        case EntityNotFoundException e -> GraphqlErrorBuilder.newError()
            .errorType(ErrorType.NOT_FOUND)
            .message(e.getMessage())
            .path(env.getExecutionStepInfo().getPath())
            .build();

        case AccessDeniedException e -> GraphqlErrorBuilder.newError()
            .errorType(ErrorType.FORBIDDEN)
            .message("Access denied")  // Never leak internal reason
            .build();

        default -> GraphqlErrorBuilder.newError()
            .errorType(ErrorType.INTERNAL_ERROR)
            .message("An unexpected error occurred")  // Never leak stack traces
            .build();
    };
}
```

### Graceful Degradation in Nested Resolvers
Return empty collections rather than propagating errors for non-critical fields:

```java
@SchemaMapping(typeName = "Entity", field = "optional")
public CompletableFuture<List<OptionalModel>> optional(EntityModel entity, DataFetchingEnvironment env) {
    return loader.load(entity.id())
        .exceptionally(ex -> {
            log.error("Optional field failed", keyValue("entityId", entity.id()), ex);
            return List.of();  // Graceful degradation
        });
}
```

## Conditional GraphQL

Enable conditionally per environment:

```java
@ConditionalOnProperty(name = "app.graphql.enabled", havingValue = "true")
@Configuration
public class GraphQLConfiguration { }
```
