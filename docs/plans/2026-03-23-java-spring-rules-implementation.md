# Java/Spring Boot Rules Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Port Java 21+ and Spring Boot 3.5+ best practices from quote-iq into cpc as reusable, project-agnostic rule sets with two new profiles.

**Architecture:** Three new rule set directories (`java`, `java-spring`, `java-spring-graphql`) following existing cpc conventions. Rules extracted from quote-iq with project-specific code converted to pseudocode and custom components generalized to principles. Two new profiles in `config.yaml`. Tests follow the `TestFlutterAppProfile` pattern in `tests/test_linker.py`.

**Tech Stack:** Markdown rule files, YAML config, Python (pytest)

---

### Task 1: Write tests for java-spring profile

Tests go first. Follow the pattern established by `TestFlutterAppProfile` in `tests/test_linker.py:374-412`.

**Files:**
- Modify: `tests/test_linker.py` (append new test classes at end of file)

**Step 1: Write the failing tests**

Add two test classes to `tests/test_linker.py`:

```python
class TestJavaSpringProfile:
    """Tests for the java-spring profile resolution."""

    def test_java_spring_profile_exists(self) -> None:
        from cpc.config import load_config

        config = load_config()
        assert "java-spring" in config.profiles

    def test_java_spring_profile_rules(self) -> None:
        from cpc.config import RuleSet, load_config

        config = load_config()
        profile = config.profiles["java-spring"]
        assert RuleSet("universal-coding") in profile.rules
        assert RuleSet("java") in profile.rules
        assert RuleSet("java-spring") in profile.rules

    def test_java_spring_profile_skills(self) -> None:
        from cpc.config import load_config

        config = load_config()
        profile = config.profiles["java-spring"]
        assert "cpc-init" in profile.skills
        assert "cpc-audit" in profile.skills
        assert "cpc-extract" in profile.skills

    def test_java_rules_discoverable(self) -> None:
        from cpc.config import RuleSet, discover_rules, load_config

        config = load_config()
        profile = config.profiles["java-spring"]
        rules = discover_rules(profile.rules)
        for rule_set in profile.rules:
            assert len(rules[rule_set]) > 0, f"No files found for rule set: {rule_set}"

    def test_java_spring_has_review_file(self) -> None:
        from cpc.config import RuleSet, discover_rules

        rules = discover_rules([RuleSet("java-spring")])
        review_files = [f for f in rules[RuleSet("java-spring")] if "review" in f.name]
        assert len(review_files) == 1


class TestJavaSpringGraphqlProfile:
    """Tests for the java-spring-graphql profile resolution."""

    def test_java_spring_graphql_profile_exists(self) -> None:
        from cpc.config import load_config

        config = load_config()
        assert "java-spring-graphql" in config.profiles

    def test_java_spring_graphql_profile_rules(self) -> None:
        from cpc.config import RuleSet, load_config

        config = load_config()
        profile = config.profiles["java-spring-graphql"]
        assert RuleSet("universal-coding") in profile.rules
        assert RuleSet("java") in profile.rules
        assert RuleSet("java-spring") in profile.rules
        assert RuleSet("java-spring-graphql") in profile.rules

    def test_java_spring_graphql_rules_discoverable(self) -> None:
        from cpc.config import discover_rules, load_config

        config = load_config()
        profile = config.profiles["java-spring-graphql"]
        rules = discover_rules(profile.rules)
        for rule_set in profile.rules:
            assert len(rules[rule_set]) > 0, f"No files found for rule set: {rule_set}"
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_linker.py::TestJavaSpringProfile -v`
Expected: FAIL — profiles don't exist yet

Run: `uv run pytest tests/test_linker.py::TestJavaSpringGraphqlProfile -v`
Expected: FAIL — profiles don't exist yet

---

### Task 2: Create `rules/java/java-jdk-21.md`

Extract from quote-iq's `java.md`. Key changes: pin to Java 21+, all examples are already generic (no quote-iq references).

**Files:**
- Create: `rules/java/java-jdk-21.md`

**Step 1: Create the rule file**

Source: `/Users/koi/Repositories/myersadamk/quote-iq/.claude/rules/java.md`

Changes from source:
- Title: "Java Style (17+)" → "Java 21+ Idioms"
- Add version pin statement at top: "Modern Java idioms targeting JDK 21+."
- Path scoping stays: `src/**/*.java`
- All examples are already generic — keep as-is
- The `ProcessingResult` record example in the Records section uses `@Builder` and `@Nullable` — keep, as these are generic patterns

**Step 2: Verify file exists and has frontmatter**

Run: `head -5 rules/java/java-jdk-21.md`
Expected: YAML frontmatter with `paths: ["src/**/*.java"]`

---

### Task 3: Create `rules/java/java-lombok.md`

Extract from quote-iq's `lombok.md`. Already fully generic — minimal changes needed.

**Files:**
- Create: `rules/java/java-lombok.md`

**Step 1: Create the rule file**

Source: `/Users/koi/Repositories/myersadamk/quote-iq/.claude/rules/lombok.md`

Changes from source:
- None required — file is already project-agnostic
- Keep path scoping: `src/**/*.java`

**Step 2: Verify file exists**

Run: `ls rules/java/`
Expected: `java-jdk-21.md  java-lombok.md`

---

### Task 4: Create `rules/java-spring/java-spring-boot.md`

Extract from quote-iq's `spring-boot.md`. Pin to Spring Boot 3.5+, generalize examples.

**Files:**
- Create: `rules/java-spring/java-spring-boot.md`

**Step 1: Create the rule file**

Source: `/Users/koi/Repositories/myersadamk/quote-iq/.claude/rules/spring-boot.md`

Changes from source:
- Title: "Spring Boot Patterns" → "Spring Boot 3.5+ Patterns"
- Add version pin: "Core patterns targeting Spring Boot 3.5+."
- Path scoping stays: `src/**/*.java`
- `ImportResult.failure()` example → generalize to the `ProcessingResult` sealed-interface pattern (reference `java-jdk-21.md` Records section)
- All class names are already generic (`Entity`, `EntityService`, `EntityRepository`) — keep

**Step 2: Verify file exists and has version pin**

Run: `grep "3.5" rules/java-spring/java-spring-boot.md`
Expected: Shows the version pin line

---

### Task 5: Create `rules/java-spring/java-spring-testing.md`

Extract from quote-iq's `spring-testing.md`. Generalize `@IntegrationTest` into a principle.

**Files:**
- Create: `rules/java-spring/java-spring-testing.md`

**Step 1: Create the rule file**

Source: `/Users/koi/Repositories/myersadamk/quote-iq/.claude/rules/spring-testing.md`

Changes from source:
- Path scoping stays: `src/test/**/*.java`
- Section "Test Annotations": add a principle statement above the example: "Create meta-annotations to bundle common test slice configurations. This reduces annotation soup and enforces consistency across test classes."
- The `@IntegrationTest` example stays as a concrete illustration of the principle
- All other examples are already generic

**Step 2: Verify path scoping**

Run: `head -5 rules/java-spring/java-spring-testing.md`
Expected: `src/test/**/*.java` in frontmatter

---

### Task 6: Create `rules/java-spring/java-spring-review.md`

New file — review checklist for Java Spring projects. Follow the pattern from `rules/python-cli/python-cli-review.md`.

**Files:**
- Create: `rules/java-spring/java-spring-review.md`

**Step 1: Create the rule file**

Pattern from: `rules/python-cli/python-cli-review.md`

Content:

```markdown
# Java Spring — Review Checklist

## Verification Commands

All MUST pass before approval:

\`\`\`bash
./gradlew test
\`\`\`

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
```

**Step 2: Verify the file references ./gradlew test**

Run: `grep "gradlew" rules/java-spring/java-spring-review.md`
Expected: `./gradlew test`

---

### Task 7: Create `rules/java-spring-graphql/java-spring-graphql.md`

Extract from quote-iq's `spring-graphql.md`. Generalize `RegisterableLoader` and `DataLoaderConfiguration` into principles.

**Files:**
- Create: `rules/java-spring-graphql/java-spring-graphql.md`

**Step 1: Create the rule file**

Source: `/Users/koi/Repositories/myersadamk/quote-iq/.claude/rules/spring-graphql.md`

Changes from source:
- Path scoping stays: `src/**/graphql/**/*.java`, `src/main/resources/graphql/**`
- "RegisterableLoader Interface" section: add principle statement: "Define a common interface for DataLoader registration so loaders are self-describing and centrally discovered via Spring's dependency injection."
- "Centralized Registration" section: add principle statement: "Centralize loader registration in a single config class rather than scattering registration across controllers. Use `@PostConstruct` to auto-register all loaders found via DI."
- All code examples stay — they're already generic enough (Entity, RelatedModel, etc.)

**Step 2: Verify file exists with correct path scoping**

Run: `head -5 rules/java-spring-graphql/java-spring-graphql.md`
Expected: Frontmatter with both graphql path patterns

---

### Task 8: Add profiles to `config.yaml`

**Files:**
- Modify: `config.yaml` (add two new profile entries)

**Step 1: Add profiles**

Add after the `flutter-app` profile block in `config.yaml`:

```yaml
  java-spring:
    rules:
      - universal-coding
      - java
      - java-spring
    skills:
      - cpc-init
      - cpc-audit
      - cpc-extract

  java-spring-graphql:
    rules:
      - universal-coding
      - java
      - java-spring
      - java-spring-graphql
    skills:
      - cpc-init
      - cpc-audit
      - cpc-extract
```

**Step 2: Verify config loads without warnings**

Run: `uv run python -c "from cpc.config import load_config; c = load_config(); print([p for p in c.profiles if 'java' in p])"`
Expected: `['java-spring', 'java-spring-graphql']`

---

### Task 9: Run all tests and verify

**Step 1: Run the new profile tests**

Run: `uv run pytest tests/test_linker.py::TestJavaSpringProfile tests/test_linker.py::TestJavaSpringGraphqlProfile -v`
Expected: All PASS

**Step 2: Run the full test suite**

Run: `uv run pytest -v`
Expected: All PASS, no regressions

**Step 3: Commit**

```bash
git add rules/java/ rules/java-spring/ rules/java-spring-graphql/ config.yaml tests/test_linker.py docs/
git commit -m "feat: add Java 21+ and Spring Boot 3.5+ rule sets and profiles

Port best practices from quote-iq into reusable, project-agnostic rule sets:
- rules/java/ — JDK 21+ idioms and Lombok conventions
- rules/java-spring/ — Spring Boot 3.5+ patterns, testing, review checklist
- rules/java-spring-graphql/ — Spring GraphQL with DataLoader patterns

Two new profiles: java-spring and java-spring-graphql.
Includes design doc, ROADMAP, and profile integration tests."
```
