# Memory Management

When and how to update `.interface-design/system.md`.

## When to Add Patterns

Add to system.md when:
- Component used 2+ times
- Pattern is reusable across the project
- Has specific measurements worth remembering

## Pattern Format

```markdown
### Button Primary
- Height: 48 logical pixels
- Padding: EdgeInsets.symmetric(horizontal: 16, vertical: 12)
- Radius: BorderRadius.circular(8)
- Text: 14sp, FontWeight.w500
- ThemeExtension field: `buttonPrimary`
```

## Don't Document

- One-off components
- Temporary experiments
- Variations better handled with widget parameters

## Pattern Reuse

Before creating a component, check system.md:
- Pattern exists? Use it.
- Need variation? Extend, don't create new.

Memory compounds: each pattern saved makes future work faster and more consistent.

---

# Validation Checks

If system.md defines specific values, check consistency:

**Spacing** — All values multiples of the defined base unit? No magic numbers in EdgeInsets or SizedBox?

**Depth** — Using the declared strategy throughout? (borders-only means no BoxShadow, shadow-based means no border-only cards)

**Colors** — Using ColorScheme roles and ThemeExtension fields, not hard-coded Color() literals?

**Tokens** — ThemeExtension fields match the documented token names? No drift between system.md and the ThemeExtension class?

**Patterns** — Reusing documented patterns instead of creating new widgets that duplicate existing ones?
