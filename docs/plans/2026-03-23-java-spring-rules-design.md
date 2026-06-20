# Java/Spring Boot Rules Design

## Goal

Port Java and Spring Boot best practices from quote-iq into cpc as reusable, project-agnostic rule sets. Capture future architectural evolution in a ROADMAP.

## Rule Set Structure

Three new rule set directories with compositional layering: `universal-coding` → `java` → `java-spring` → optionally `java-spring-graphql`.

```
rules/
├── java/                      # Pure Java 21+ idioms (no framework dependency)
│   ├── java-jdk-21.md         # Modern Java idioms, records, sealed types, pattern matching
│   └── java-lombok.md         # Lombok conventions (records over @Data, @RequiredArgsConstructor)
├── java-spring/               # Spring Boot 3.5+ patterns
│   ├── java-spring-boot.md    # DI, layering, config, transactions, error handling, security
│   ├── java-spring-testing.md # Test slicing, meta-annotations, TestContainers, MockMvc
│   └── java-spring-review.md  # Verification: ./gradlew test
└── java-spring-graphql/       # Optional GraphQL add-on
    └── java-spring-graphql.md # DataLoader, schema mapping, error handling
```

### Path Scoping (frontmatter)

- `java-jdk-21.md`, `java-lombok.md`, `java-spring-boot.md` → `src/**/*.java`
- `java-spring-testing.md` → `src/test/**/*.java`
- `java-spring-graphql.md` → `src/**/graphql/**/*.java`, `src/main/resources/graphql/**`

## Profiles

```yaml
java-spring:
  rules: [universal-coding, java, java-spring]
  skills: [cpc-init, cpc-audit, cpc-extract]

java-spring-graphql:
  rules: [universal-coding, java, java-spring, java-spring-graphql]
  skills: [cpc-init, cpc-audit, cpc-extract]
```

## Extraction Principles

### Project-Specific Code → Pseudocode

All examples from quote-iq are converted to pseudocode or generic domain-neutral examples. No project-specific class names, packages, or business logic.

### Custom Components → General Principles

| Custom Component | Generalized Principle |
|---|---|
| `@IntegrationTest` composite annotation | "Create meta-annotations to bundle common test slice configurations — reduces annotation soup and enforces consistency" |
| `RegisterableLoader<K, V>` interface | "Define a common interface for DataLoader registration so loaders are self-describing and centrally discovered" |
| `ProcessingResult` / `ProcessingError` | Sealed interface + error enum pattern for result types over exceptions for expected failures |
| `ImportResult` failure pattern | Folded into the ProcessingResult pattern |
| `DataLoaderConfiguration` with `@PostConstruct` | "Centralize loader registration in a single config class rather than scattering across controllers" |

### Version Pins

Version minimums are stated in the rule files themselves (e.g. "This rule targets Java 21+" at the top of `java-jdk-21.md`, "Spring Boot 3.5+" in `java-spring-boot.md`). They are not injected into generated CLAUDE.md sections.

## What This Design Does NOT Include

- Rules → skills migration (ROADMAP item)
- Dispatchable review/coding/design agents (ROADMAP item)
- JDK feature dictionary or version upgrade auditing (ROADMAP item)
- Session continuity for teams (ROADMAP item)
- Context-aware rule loading based on conversation intent (ROADMAP item)
