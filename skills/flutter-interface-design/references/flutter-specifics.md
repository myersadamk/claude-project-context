# Flutter-Specific Design Guidance

Flutter-specific concerns that don't have equivalents in web interface design.

---

## Material Design Tension

Material Design gives you a complete system. The trap is accepting it wholesale.

Material's defaults are recognizable — they look like Google apps. For a product that should feel like *your* product, you need to override strategically. Use Material's infrastructure (ThemeData, ColorScheme, TextTheme) but replace its aesthetic decisions.

**Override aggressively:**
- Typography — Material's default type scale is rarely what your product needs. Replace via `TextTheme` with your own sizes, weights, and tracking.
- Color — `ColorScheme.fromSeed()` is a starting point, not a destination. Override individual roles to match your product's world.
- Shape — Material's rounded rectangles have a specific personality. Adjust `ShapeBorder` values to match your intent.
- Elevation — Material's shadow system is heavy. Consider borders-only or subtle single shadows instead.

**Keep Material's infrastructure:**
- `ThemeData` and `Theme.of(context)` for propagation
- `ColorScheme` role names (primary, surface, onSurface, etc.)
- `TextTheme` level names (headlineLarge, bodyMedium, etc.)
- `InkWell`/`InkResponse` for interaction feedback

The goal: Material's plumbing, your product's personality.

---

## Platform-Adaptive Design

Flutter runs everywhere. The question is whether to look native or consistent.

**Material everywhere** — One design language across platforms. Simpler to maintain, consistent brand. Works when your product's identity matters more than platform conventions.

**Platform-adaptive** — Use `.adaptive` constructors and `Platform` checks to match iOS (Cupertino) and Android (Material) conventions. Works for utility apps where users expect platform-native behavior.

**Hybrid** — Material foundation with platform-adaptive navigation, scrolling physics, and system UI integration. Most common for production apps.

Key platform differences to respect:
- **Navigation** — iOS: edge swipe back, bottom tabs. Android: system back, drawer or rail.
- **Scrolling** — iOS: bounce. Android: glow/stretch overscroll.
- **Typography** — iOS: SF Pro. Android: Roboto. Consider Google Fonts for a unified choice.
- **System UI** — Status bar, navigation bar styling via `SystemUiOverlayStyle`.

---

## Widget Composition

Flutter's widget tree is your design tool. Composition over configuration.

**Prefer specific widgets over Container:**
```dart
// Craft — each widget has one job
DecoratedBox(
  decoration: BoxDecoration(
    color: theme.colorScheme.surface,
    borderRadius: BorderRadius.circular(8),
  ),
  child: Padding(
    padding: EdgeInsets.all(16),
    child: content,
  ),
)

// Avoid — Container hides multiple responsibilities
Container(
  decoration: BoxDecoration(...),
  padding: EdgeInsets.all(16),
  child: content,
)
```

**Why this matters for design:** When each widget has one job, you can read the widget tree like a design spec. `DecoratedBox` = surface treatment. `Padding` = spacing. `SizedBox` = dimension. The intent is visible in the structure.

**SizedBox for spacing:**
```dart
// Between items in a Column
SizedBox(height: 16),

// Between items in a Row
SizedBox(width: 12),
```

Prefer `SizedBox` over `Padding` for gaps between siblings — it reads as "space" rather than "this element's inset."

---

## ThemeExtension for Custom Tokens

`ColorScheme` covers Material's built-in roles. Your product needs more.

```dart
class AppTokens extends ThemeExtension<AppTokens> {
  final Color surfaceElevated;
  final Color surfaceOverlay;
  final Color borderSubtle;
  final Color borderStrong;
  final Color textTertiary;
  final Color textMuted;
  final double spacingBase;
  final double radiusSmall;
  final double radiusMedium;

  // ... constructor, copyWith, lerp
}
```

Access anywhere via:
```dart
final tokens = Theme.of(context).extension<AppTokens>()!;
```

**Token naming:** Names should evoke the product's world. `surfaceElevated` and `borderSubtle` describe function. If your tokens could belong to any app, they're not designed — they're infrastructure.

**Register in ThemeData:**
```dart
ThemeData(
  extensions: [
    AppTokens(
      surfaceElevated: Color(0xFF1A1A2E),
      borderSubtle: Colors.white.withValues(alpha: 0.06),
      // ...
    ),
  ],
)
```

---

## State-Driven Theming

Flutter's theming system supports light/dark and beyond.

**ThemeMode** — `ThemeMode.system`, `.light`, `.dark`. Wire to `MaterialApp`'s `themeMode` parameter.

**ColorScheme.fromSeed** — Quick palette generation. Override individual roles after generation for precision.

**Brightness-aware tokens:**
```dart
AppTokens lightTokens = AppTokens(
  surfaceElevated: Color(0xFFFFFFFF),
  borderSubtle: Colors.black.withValues(alpha: 0.08),
);

AppTokens darkTokens = AppTokens(
  surfaceElevated: Color(0xFF1E1E2E),
  borderSubtle: Colors.white.withValues(alpha: 0.06),
);
```

Dark mode specifics:
- Higher elevation = slightly lighter surfaces (not darker)
- Borders carry more structural weight than shadows
- Semantic colors (error, success) need slight desaturation
- Text hierarchy still applies — just with inverted contrast

---

## Animation

Flutter has excellent animation support. Use it with restraint.

**Implicit animations first:**
- `AnimatedContainer`, `AnimatedOpacity`, `AnimatedAlign`, `AnimatedPadding`
- These handle the common cases without controller boilerplate
- Default to `Curves.easeOutCubic` and 200ms duration

**Duration guidance:**
- Micro-interactions (hover, press): 100-150ms
- State transitions (expand, collapse): 200-250ms
- Page transitions: 300ms
- Complex choreography: 400-500ms

**Curve guidance:**
- `Curves.easeOutCubic` — default for most transitions
- `Curves.easeInOut` — symmetrical, good for toggles
- `Curves.fastOutSlowIn` — Material's recommended curve
- Avoid `Curves.bounceOut` or `Curves.elasticOut` in professional interfaces

**Accessibility:**
- Respect `MediaQuery.of(context).disableAnimations`
- Provide `Duration.zero` alternatives when reduce-motion is requested
- Never convey meaning through animation alone
