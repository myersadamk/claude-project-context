# Core Craft Principles

These apply regardless of design direction. This is the quality floor.

---

## Surface & Token Architecture

Professional interfaces don't pick colors randomly — they build systems. Understanding this architecture is the difference between "looks okay" and "feels like a real product."

### The Primitive Foundation

Every color in your interface should trace back to a small set of primitives:

- **Foreground** — text colors (primary, secondary, muted) via `ColorScheme.onSurface` and ThemeExtension
- **Background** — surface colors (base, elevated, overlay) via `ColorScheme.surface` and ThemeExtension
- **Border** — edge colors (default, subtle, strong) via ThemeExtension
- **Brand** — your primary accent via `ColorScheme.primary`
- **Semantic** — functional colors (error, warning, success) via `ColorScheme.error` and ThemeExtension

Don't invent new colors. Map everything to these primitives.

### Surface Elevation Hierarchy

Surfaces stack. A dropdown sits above a card which sits above the page. Build a numbered system:

```
Level 0: Base background (the app canvas) — ColorScheme.surface
Level 1: Cards, panels (same visual plane) — tokens.surfaceElevated
Level 2: Dropdowns, popovers (floating above) — tokens.surfaceOverlay
Level 3: Nested dropdowns, stacked overlays
Level 4: Highest elevation (rare)
```

In dark mode, higher elevation = slightly lighter. In light mode, higher elevation = slightly lighter or uses shadow. The principle: **elevated surfaces need visual distinction from what's beneath them.**

### The Subtlety Principle

This is where most interfaces fail. Study Vercel, Supabase, Linear — their surfaces are **barely different** but still distinguishable.

**For surfaces:** The difference between elevation levels should be subtle — a few percentage points of lightness, not dramatic jumps.

```dart
// Dark mode surface progression — whisper-quiet shifts
final surface0 = Color(0xFF0A0A0F);     // base
final surface1 = Color(0xFF12121A);     // ~7% lighter
final surface2 = Color(0xFF161620);     // ~9% lighter
final surface3 = Color(0xFF1A1A26);     // ~12% lighter
```

**For borders:** Use low opacity so they blend with their background:

```dart
// Dark mode borders — disappear when you're not looking
final borderDefault = Colors.white.withValues(alpha: 0.08);
final borderSubtle  = Colors.white.withValues(alpha: 0.05);
final borderStrong  = Colors.white.withValues(alpha: 0.12);
final borderFocus   = colorScheme.primary.withValues(alpha: 0.5);
```

**Common mistakes to avoid:**
- Borders that are too visible (`Border.all(color: Colors.grey)` instead of subtle alpha)
- Surface jumps that are too dramatic
- Using different hues for different surfaces (gray card on blue background)
- Harsh dividers where subtle borders would do

### Text Hierarchy via Tokens

Don't just have "text" and "gray text." Build four levels:

```dart
// Access via TextTheme + color overrides
final primary   = colorScheme.onSurface;                          // highest contrast
final secondary = colorScheme.onSurface.withValues(alpha: 0.7);   // supporting text
final tertiary  = colorScheme.onSurface.withValues(alpha: 0.5);   // metadata, timestamps
final muted     = colorScheme.onSurface.withValues(alpha: 0.35);  // disabled, placeholder
```

Use all four consistently. If you're only using two, your hierarchy is too flat.

### Border Progression

Borders aren't binary. Build a scale using `BoxDecoration`:

```dart
// Standard separation
BoxDecoration(
  border: Border.all(color: tokens.borderDefault),
  borderRadius: BorderRadius.circular(tokens.radiusMedium),
)

// Emphasis — hover states, active elements
BoxDecoration(
  border: Border.all(color: tokens.borderStrong),
  borderRadius: BorderRadius.circular(tokens.radiusMedium),
)

// Maximum emphasis — focus rings
BoxDecoration(
  border: Border.all(color: tokens.borderFocus, width: 2),
  borderRadius: BorderRadius.circular(tokens.radiusMedium),
)
```

Match border intensity to the importance of the boundary.

### Dedicated Control Tokens

Form controls (TextFields, Checkboxes, DropdownButtons) have specific needs. Don't just reuse surface tokens:

```dart
class ControlTokens extends ThemeExtension<ControlTokens> {
  final Color controlBackground;   // often darker than surface
  final Color controlBorder;       // needs to feel interactive
  final Color controlBorderFocus;  // clear focus indication
  final Color controlFill;         // selected/checked state
}
```

This separation lets you tune controls independently from layout surfaces.

---

## Spacing System

Pick a base unit and stick to multiples. Define constants:

```dart
abstract class Spacing {
  static const double xs  = 4;   // micro: icon gaps, tight pairs
  static const double sm  = 8;   // component: within buttons, inputs
  static const double md  = 16;  // section: between related groups
  static const double lg  = 24;  // major: between distinct sections
  static const double xl  = 32;  // page: top-level separation
  static const double xxl = 48;  // hero: major visual breaks
}
```

Use via `SizedBox` for gaps and `EdgeInsets` for padding:

```dart
// Gap between items
SizedBox(height: Spacing.md),

// Card padding
Padding(
  padding: EdgeInsets.all(Spacing.md),
  child: content,
)

// Asymmetric only when content requires it
Padding(
  padding: EdgeInsets.symmetric(
    horizontal: Spacing.md,
    vertical: Spacing.sm,
  ),
  child: buttonContent,
)
```

## Symmetrical Padding

Padding should be balanced. If top is 16, the other sides should match unless content naturally requires asymmetry.

```dart
// Good — balanced
EdgeInsets.all(16)
EdgeInsets.symmetric(horizontal: 16, vertical: 12)  // only when horizontal needs room

// Bad — arbitrary asymmetry
EdgeInsets.fromLTRB(16, 24, 16, 12)
```

## Border Radius Consistency

Sharper corners feel technical. Rounder corners feel friendly. Build a scale:

```dart
abstract class Radii {
  static const double sm = 4;   // inputs, buttons
  static const double md = 8;   // cards
  static const double lg = 12;  // modals, large containers
  static const double xl = 16;  // hero cards, onboarding
}
```

Don't mix sharp and soft randomly — inconsistent radius is as jarring as inconsistent spacing.

## Depth & Elevation Strategy

Choose ONE approach and commit:

**Borders-only (flat)** — Clean, technical, dense. For utility-focused tools where information density matters.

```dart
BoxDecoration(
  border: Border.all(color: tokens.borderDefault),
  borderRadius: BorderRadius.circular(Radii.md),
)
```

**Subtle single shadows** — Soft lift without complexity:

```dart
BoxDecoration(
  borderRadius: BorderRadius.circular(Radii.md),
  boxShadow: [
    BoxShadow(
      color: Colors.black.withValues(alpha: 0.08),
      blurRadius: 3,
      offset: Offset(0, 1),
    ),
  ],
)
```

**Layered shadows** — Rich, premium, dimensional:

```dart
BoxDecoration(
  borderRadius: BorderRadius.circular(Radii.md),
  boxShadow: [
    BoxShadow(
      color: Colors.black.withValues(alpha: 0.04),
      blurRadius: 2,
      offset: Offset(0, 1),
    ),
    BoxShadow(
      color: Colors.black.withValues(alpha: 0.03),
      blurRadius: 4,
      offset: Offset(0, 2),
    ),
    BoxShadow(
      color: Colors.black.withValues(alpha: 0.02),
      blurRadius: 8,
      offset: Offset(0, 4),
    ),
  ],
)
```

**Surface color shifts** — Background tints establish hierarchy without shadows.

Don't mix approaches.

## Card Layouts

A metric card doesn't have to look like a plan card doesn't have to look like a settings card. Design each card's internal structure for its specific content — but keep the surface treatment consistent: same border weight, shadow depth, corner radius, padding scale.

## Typography Hierarchy

Build distinct levels distinguishable at a glance:

```dart
TextTheme(
  headlineLarge: TextStyle(
    fontSize: 28,
    fontWeight: FontWeight.w600,
    letterSpacing: -0.5,  // tight tracking for presence
    height: 1.2,
  ),
  bodyLarge: TextStyle(
    fontSize: 16,
    fontWeight: FontWeight.w400,
    height: 1.5,  // comfortable for reading
  ),
  labelMedium: TextStyle(
    fontSize: 12,
    fontWeight: FontWeight.w500,
    letterSpacing: 0.5,  // open tracking for small sizes
  ),
)
```

Don't rely on size alone. Combine size, weight, and letterSpacing to create clear hierarchy.

## Monospace for Data

Numbers, IDs, codes, timestamps belong in monospace with tabular figures:

```dart
Text(
  '1,234.56',
  style: TextStyle(
    fontFamily: 'JetBrains Mono',  // or your chosen mono
    fontFeatures: [FontFeature.tabularFigures()],
  ),
)
```

## Iconography

Icons clarify, not decorate — if removing an icon loses no meaning, remove it. Choose one icon set (`Icons`, `CupertinoIcons`, or a package like `lucide_icons`) and stick with it throughout.

## Animation

Keep it fast and functional. Micro-interactions should feel instant (~150ms). Larger transitions can be slightly longer (~250ms). Use `Curves.easeOutCubic`. Avoid bounce/elastic in professional interfaces.

## Color Carries Meaning

Gray builds structure. Color communicates — status, action, emphasis, identity. Unmotivated color is noise. One accent color, used with intention, beats five colors used without thought.

## Navigation Context

Screens need grounding. A data table floating in space feels like a component demo, not a product. Include:

- **Navigation** — `NavigationRail`, `NavigationBar`, or custom sidebar showing location
- **Location indicator** — breadcrumbs, page title, or active nav state
- **User context** — who's logged in, what workspace/org

When building sidebars, consider using the same surface color as the main content with a subtle `Border` for separation.

## Dark Mode

Dark interfaces have different needs:

**Borders over shadows** — `BoxShadow` is less visible on dark backgrounds. Lean on `Border.all()` for definition.

**Adjust semantic colors** — Status colors often need slight desaturation:

```dart
// Light mode
final successLight = Color(0xFF22C55E);

// Dark mode — desaturated
final successDark = Color(0xFF4ADE80).withValues(alpha: 0.9);
```

**Same structure, different values** — The hierarchy system still applies, just with inverted values. Wire both light and dark `AppTokens` into `ThemeData`.
