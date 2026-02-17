# UI Best Practices

## Accessibility

- Custom interactive widgets MUST be wrapped with `Semantics` when meaning isn't implicit
- Touch targets MUST be at least 48x48 logical pixels (Material minimum)
- Color MUST NOT be the sole indicator of state (pair with icon or text)
- MUST use `ExcludeSemantics` / `MergeSemantics` to keep the accessibility tree clean
- Icon-only buttons MUST have `tooltip` or `Semantics(label:)`
- MUST verify contrast against the actual surface — not just the scaffold background
- When using opacity modifiers (e.g., `withValues(alpha: 0.7)`), MUST calculate the blended color against the surface to verify contrast

## Responsiveness

- MUST use `LayoutBuilder` or `MediaQuery` for responsive layouts, not hard-coded breakpoints
- MUST test at multiple widths: compact (<600), medium (600-840), expanded (>840)
- MUST NOT produce horizontal overflow at any size
- MUST prefer `Flexible` / `Expanded` over fixed widths for content areas
- Navigation MUST adapt: `NavigationBar` (compact) vs `NavigationRail` (medium) vs sidebar (expanded)

## Motion

- Transitions MUST use design-system duration and curve tokens (see local `system.md`)
- MUST respect `MediaQuery.of(context).disableAnimations` — provide `Duration.zero` alternative
- MUST NOT cause layout shift on hover — use `Transform` or `AnimatedScale` only
- MUST NOT use auto-playing animations, parallax, or infinite loops
- MUST prefer implicit animations (`AnimatedContainer`, `AnimatedOpacity`) over explicit controllers

### Banned Effects

- Glassmorphism (frosted glass / `BackdropFilter` for decoration)
- Infinite gradient animations
- Heavy glow/blur effects (`ImageFilter.blur` for decoration)
- Parallax scrolling
- Auto-playing carousels
- `Curves.bounceOut` or `Curves.elasticOut` in professional interfaces

## Theming

- MUST access colors via `Theme.of(context).colorScheme` or ThemeExtension — no hard-coded `Color()` literals
- MUST access text styles via `Theme.of(context).textTheme` with `copyWith()` for overrides
- MUST define custom tokens via `ThemeExtension`, not ad-hoc constants
- MUST support both light and dark `ThemeData`
- MUST NOT use `Theme.of(context).primaryColor` or other deprecated theme properties
