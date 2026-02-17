# Flutter App — Review Checklist

## Verification Commands

All MUST pass before approval:

```bash
flutter analyze && flutter test
```

## Checklist

### Dart Quality (-> flutter-app-best-practices.md)

- [ ] No `dynamic` types without justification
- [ ] `const` constructors used wherever possible
- [ ] Controllers and streams disposed properly
- [ ] Specific widgets preferred over Container
- [ ] File size under 200 lines or extraction justified

### Accessibility (-> flutter-app-ui.md)

- [ ] Semantics widgets on custom interactive elements
- [ ] Touch targets at least 48x48 logical pixels
- [ ] Color not sole indicator of meaning
- [ ] Keyboard/focus traversal works logically

### Theming (-> flutter-app-ui.md)

- [ ] No hard-coded Color() literals in widget code
- [ ] Text styles accessed via Theme.of(context).textTheme
- [ ] Custom tokens via ThemeExtension, not ad-hoc constants
- [ ] Both light and dark ThemeData supported

### Design System (-> flutter-app-design-system.md)

- [ ] `flutter-interface-design` skill invoked for new UI work
- [ ] Colors use ColorScheme roles or ThemeExtension tokens
- [ ] Spacing follows defined scale (multiples of base unit)
- [ ] Typography matches defined TextTheme levels
- [ ] Depth uses the declared strategy consistently
- [ ] Skip if `.interface-design/system.md` is not yet populated

### Motion (-> flutter-app-ui.md)

- [ ] Durations and curves from design system tokens
- [ ] `disableAnimations` respected
- [ ] No banned effects (glassmorphism, parallax, auto-play)

### Platform

- [ ] Review against active platform conventions (Material, Cupertino, or hybrid)
- [ ] System UI styling (status bar, navigation bar) appropriate
