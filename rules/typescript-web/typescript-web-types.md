# TypeScript Best Practices

## Strict Mode Is Non-Negotiable

Projects MUST use strict TypeScript configuration. MUST NOT loosen it.
Strict mode catches nullability bugs, implicit `any`, and unreachable code
at compile time rather than in production.

## Prefer `unknown` Over `any`

`any` disables the type checker entirely — it's a hole in your safety net.
`unknown` forces you to narrow before use, which means bugs surface at
compile time.

```ts
// Avoid
function parse(data: any) {
  return data.title;
}

// Prefer
function parse(data: unknown): string {
  if (typeof data === "object" && data !== null && "title" in data) {
    return String(data.title);
  }
  throw new Error("Invalid data");
}
```

## Type Narrowing Over Casting

`as` tells the compiler "trust me" — it won't catch mistakes.
Narrowing with type guards proves the type is correct at runtime.

```ts
// Avoid
const el = document.querySelector(".nav") as HTMLElement;

// Prefer
const el = document.querySelector(".nav");
if (!(el instanceof HTMLElement)) throw new Error("Missing .nav");
```

## Name Types Clearly

- Interfaces for object shapes: `interface PageProps { ... }`
- Type aliases for unions/utilities: `type Status = 'draft' | 'published'`
- No `I` prefix on interfaces. No `T` prefix on types
- Props interfaces named: `ComponentNameProps`
- MUST export types from the file that owns the data
- MUST NOT create `types.ts` grab-bag files

## Functions

- Explicit return types on ALL functions — prevents drift, documents intent
- Prefer named functions over arrow functions at module scope

## Anti-Patterns

These MUST NOT appear in the codebase:

| Pattern | Why | Use Instead |
| --- | --- | --- |
| `any` | Disables type checking | `unknown` + narrowing |
| `as` casting | Bypasses type safety | Type guards |
| `!` non-null assertion | Hides null bugs | Handle the null case |
| `// @ts-ignore` | Silences real errors | Fix the type error |
| `// @ts-expect-error` | Only with linked issue | Fix the type error or add issue link |
| Barrel files (`index.ts` re-exports) | Obscures imports | Direct imports |
| Enums | Runtime overhead, quirky behavior | `as const` objects or union types |
