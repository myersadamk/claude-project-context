# Expo Web Review

## Verification Commands

These MUST pass before any PR or task completion:

```bash
npx expo lint
npx tsc --noEmit
npx jest
npx expo export --platform web
```

## Checklist

### Correctness
- [ ] Route files are in `app/` and follow Expo Router conventions -> expo-web-framework.md
- [ ] Layouts in `_layout.tsx`, screen-specific logic in route files
- [ ] Platform-specific code uses `Platform.select()` or `.native.tsx` / `.web.tsx` extensions
- [ ] No React/RN imports in pure-logic modules -> typescript-web-best-practices.md

### Styling
- [ ] Nativewind classes used consistently -> expo-web-nativewind.md
- [ ] Styling follows semantic token conventions -> typescript-web-styling.md
- [ ] Tested on web viewport AND mobile simulator (if applicable)

### State
- [ ] Zustand stores follow one-per-domain pattern -> typescript-web-state.md
- [ ] Persistence configured for target platform -> expo-web-zustand.md

### Security
- [ ] No secrets in client code -> universal-coding-security.md
- [ ] External data validated at API boundary -> typescript-web-best-practices.md

### Types
- [ ] No `any` — use `unknown` and narrow -> typescript-web-types.md
- [ ] Route params typed -> expo-web-framework.md

### Exceptions
- Any rule exception MUST include a code comment with justification
- Discuss before merging
