# UI Best Practices

## Semantic HTML

- MUST use landmark elements: `<header>`, `<nav>`, `<main>`, `<footer>`, `<aside>`
- Headings MUST follow hierarchy: one `<h1>` per page, no skipped levels
- MUST use `<button>` for actions, `<a>` for navigation — MUST NOT swap them
- MUST use lists for repeated items. Tables for tabular data. Not for layout

## Accessibility

- All images MUST have descriptive `alt` (empty `alt=""` only for decorative images)
- Interactive elements MUST be keyboard accessible (Tab, Enter, Escape)
- Focus states MUST be visible on all interactive elements
- Icon-only buttons MUST have ARIA labels
- Color MUST NOT be the sole indicator of state (pair with icon or text)
- MUST maintain WCAG AA contrast minimum (4.5:1 for normal text)

## Responsiveness

- Mobile-first: base styles are mobile, layer up with breakpoints
- Touch targets MUST be minimum 44x44px on mobile
- MUST NOT produce horizontal scroll at any viewport width
- Test at 320px, 768px, 1024px, 1440px

## Motion

- Transitions MUST use design-system motion tokens (see local `design-system.md`)
- MUST respect `prefers-reduced-motion` — wrap animations in media query or use framework utility
- MUST NOT cause layout shift on hover — use `transform` only
- MUST NOT use auto-playing animations, parallax, or infinite loops

### Banned Effects

- Glassmorphism (frosted glass)
- Infinite gradient animations
- Heavy glow/blur effects
- Parallax scrolling
- Auto-playing carousels

## CSS

- MUST NOT add global CSS except design tokens and prose in the project's global stylesheet
- MUST NOT use `!important` — restructure the component instead
- All styling through Tailwind utilities — no inline `style` attributes
