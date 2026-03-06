# Nativewind Rules

## Setup

- MUST use Nativewind v4+ with Expo SDK 52+
- Babel and Metro config MUST include Nativewind presets — do not manually configure
- `tailwind.config.ts` MUST include `./app/**/*.tsx` and `./src/**/*.tsx` in content paths
- MUST wrap root layout with the required CSS import or `<NativeWindStyleSheet>`

## Usage

- MUST use `className` prop for all styling — not `style` prop
- When `className` is not supported on a third-party component, wrap it or use `styled()`
- MUST NOT mix `className` and `style` on the same element unless bridging an imperative library
- Class merging: use `twMerge` or equivalent for conditional/override classes

## Platform Divergences

- Shadows: `shadow-*` classes work on web but not iOS/Android — use `elevation` or platform-specific shadow utilities
- Hover states: `hover:` prefix works on web only — MUST NOT rely on hover for essential interactions
- CSS Grid: not supported in RN — use flexbox (`flex`, `flex-row`, `flex-wrap`, `gap-*`)
- Percentage widths: prefer fractional (`w-1/2`, `w-1/3`) over percentage — more predictable cross-platform
- Gradients: not natively supported — use `expo-linear-gradient` and style prop for native, Nativewind for web

## Responsive

- Mobile-first: bare utilities target smallest viewport
- Standard breakpoints (`sm:`, `md:`, `lg:`) work on web via media queries
- On native, breakpoints resolve via screen dimensions — test on multiple device sizes
- MUST NOT assume breakpoints behave identically to CSS media queries on native

## Anti-Patterns

- MUST NOT use `@apply` — not supported in Nativewind
- MUST NOT use arbitrary values (`w-[347px]`) without documented justification
- MUST NOT use `display: none` to hide platform-specific content — use file extensions instead
- MUST NOT use web-only CSS features (`:has()`, `:is()`, CSS variables in classes) in shared components
