# Styling Principles

## Colors

- All colors MUST use semantic tokens (CSS custom properties or theme variables)
- MUST NOT hard-code hex, rgb, or hsl values — always reference tokens
- Use opacity modifiers on token colors when available

## Spacing

- MUST follow the project's defined spacing scale (see local `design-system.md`)
- MUST NOT use arbitrary/magic-number values without a code comment explaining why
- Prefer consistent gap utilities over mixed margin/padding

## Shadows

- MUST follow shadow levels defined in the project's `design-system.md`
- Prefer borders over shadows for visual separation

## Motion & Animation

- Duration and easing MUST use design-system motion tokens
- MUST respect `prefers-reduced-motion` — disable or reduce all non-essential animation
- MUST NOT use infinite animations, parallax, or auto-playing motion

## Responsive

- Mobile-first: base styles target the smallest viewport, layer up with breakpoints
- MUST test on at least two viewport sizes (mobile + desktop or tablet)

## General

- MUST NOT use `!important`
- MUST NOT use arbitrary values without a documented reason in a code comment
- See the framework-specific file (Tailwind, Nativewind) for implementation syntax and class conventions
