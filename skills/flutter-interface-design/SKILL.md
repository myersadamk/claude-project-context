---
name: flutter-interface-design
description: Design engineering for Flutter apps — craft, memory, consistency. For dashboards, apps, tools — not marketing sites.
user-invocable: true
disable-model-invocation: true
---

# Flutter Interface Design

Build Flutter interface design with craft and consistency.

## Scope

**Use for:** Dashboards, admin panels, SaaS apps, tools, settings pages, data interfaces — built with Flutter.

**Not for:** Landing pages, marketing sites, campaigns.

---

# The Problem

You will generate generic output. Your training has seen thousands of dashboards. The patterns are strong.

You can follow the entire process below — explore the domain, name a signature, state your intent — and still produce a template. Warm colors on cold structures. Friendly fonts on generic layouts. "Kitchen feel" that looks like every other app.

This happens because intent lives in prose, but code generation pulls from patterns. The gap between them is where defaults win.

The process below helps. But process alone doesn't guarantee craft. You have to catch yourself.

---

# Where Defaults Hide

Defaults don't announce themselves. They disguise themselves as infrastructure — the parts that feel like they just need to work, not be designed.

**Typography feels like a container.** Pick something readable, move on. But typography isn't holding your design — it IS your design. The weight of a headline, the personality of a label, the texture of a paragraph. These shape how the product feels before anyone reads a word. A bakery management tool and a trading terminal might both need "clean, readable type" — but the type that's warm and handmade is not the type that's cold and precise. If you're reaching for `TextTheme` defaults without overriding, you're not designing.

**Navigation feels like scaffolding.** Build the `NavigationRail`, add the destinations, get to the real work. But navigation isn't around your product — it IS your product. Where you are, where you can go, what matters most. A page floating in space is a component demo, not software.

**Data feels like presentation.** You have numbers, show numbers. But a number on screen is not design. The question is: what does this number mean to the person looking at it? A progress ring and a stacked label both show "3 of 10" — one tells a story, one fills space.

**Token names feel like implementation detail.** But your ThemeExtension fields are design decisions. `surfaceParchment` and `inkPrimary` evoke a world. `surface1` and `gray700` evoke a template. Someone reading only your token class should be able to guess what product this is.

The trap is thinking some decisions are creative and others are structural. There are no structural decisions. Everything is design. The moment you stop asking "why this?" is the moment defaults take over.

---

# Intent First

Before touching code, answer these. Not in your head — out loud, to yourself or the user.

**Who is this human?**
Not "users." The actual person. Where are they when they open this? What's on their mind? What did they do 5 minutes ago, what will they do 5 minutes after? A teacher at 7am with coffee is not a developer debugging at midnight is not a founder between investor meetings. Their world shapes the interface.

**What must they accomplish?**
Not "use the dashboard." The verb. Grade these submissions. Find the broken deployment. Approve the payment. The answer determines what leads, what follows, what hides.

**What should this feel like?**
Say it in words that mean something. "Clean and modern" means nothing — every AI says that. Warm like a notebook? Cold like a terminal? Dense like a trading floor? Calm like a reading app? The answer shapes color, type, spacing, density — everything.

If you cannot answer these with specifics, stop. Ask the user. Do not guess. Do not default.

## Every Choice Must Be A Choice

For every decision, you must be able to explain WHY.

- Why this layout and not another?
- Why this color temperature?
- Why this typeface?
- Why this spacing scale?
- Why this information hierarchy?

If your answer is "it's common" or "it's clean" or "it works" — you haven't chosen. You've defaulted.

**The test:** If you swapped your choices for the most common alternatives and the design didn't feel meaningfully different, you never made real choices.

## Sameness Is Failure

If another AI, given a similar prompt, would produce substantially the same output — you have failed.

This is not about being different for its own sake. It's about the interface emerging from the specific problem, the specific user, the specific context. When you design from intent, sameness becomes impossible because no two intents are identical.

## Intent Must Be Systemic

Saying "warm" and using cold colors is not following through. Intent is not a label — it's a constraint that shapes every decision.

If the intent is warm: surfaces, text, borders, accents, semantic colors, typography — all warm. If the intent is dense: spacing, type size, information architecture — all dense. If the intent is calm: motion, contrast, color saturation — all calm.

Check your output against your stated intent. Does every token reinforce it? Or did you state an intent and then default anyway?

---

# Product Domain Exploration

This is where defaults get caught — or don't.

Generic output: Task type -> Visual template -> Theme
Crafted output: Task type -> Product domain -> Signature -> Structure + Expression

The difference: time in the product's world before any visual or structural thinking.

## Required Outputs

**Do not propose any direction until you produce all four:**

**Domain:** Concepts, metaphors, vocabulary from this product's world. Not features — territory. Minimum 5.

**Color world:** What colors exist naturally in this product's domain? Not "warm" or "cool" — go to the actual world. If this product were a physical space, what would you see? What colors belong there that don't belong elsewhere? List 5+.

**Signature:** One element — visual, structural, or interaction — that could only exist for THIS product. If you can't name one, keep exploring.

**Defaults:** 3 obvious choices for this interface type — visual AND structural. You can't avoid patterns you haven't named.

## Proposal Requirements

Your direction must explicitly reference:
- Domain concepts you explored
- Colors from your color world exploration
- Your signature element
- What replaces each default

**The test:** Read your proposal. Remove the product name. Could someone identify what this is for? If not, it's generic. Explore deeper.

---

# The Mandate

**Before showing the user, look at what you made.**

Ask yourself: "If they said this lacks craft, what would they mean?"

That thing you just thought of — fix it first.

Your first output is probably generic. That's normal. The work is catching it before the user has to.

## The Checks

Run these against your output before presenting:

- **The swap test:** If you swapped the typeface for your usual one, would anyone notice? If you swapped the layout for a standard dashboard template, would it feel different?

- **The squint test:** Blur your eyes. Can you still perceive hierarchy? Is anything jumping out harshly? Craft whispers.

- **The signature test:** Can you point to five specific elements where your signature appears? Not "the overall feel" — actual widgets.

- **The token test:** Read your ThemeExtension fields out loud. Do they sound like they belong to this product's world, or could they belong to any project?

If any check fails, iterate before showing.

---

# Craft Foundations

## Subtle Layering

This is the backbone of craft. Regardless of direction, product type, or visual style — this principle applies to everything. You should barely notice the system working.

### Surface Elevation

Surfaces stack. Build a numbered system — base, then increasing elevation levels. In dark mode, higher elevation = slightly lighter. In light mode, higher elevation = slightly lighter or uses shadow.

Each jump should be only a few percentage points of lightness. Whisper-quiet shifts that you feel rather than see.

**Key decisions:**
- **Sidebars:** Same `ColorScheme.surface` as canvas, not different. A subtle `Border` is enough separation.
- **Dropdowns:** One level above their parent surface via ThemeExtension elevation tokens.
- **Inputs:** Slightly darker than surroundings via `InputDecorationTheme`. A darker fill signals "type here" without heavy borders.

### Borders

Low opacity `Color.withValues(alpha:)` blends with the background — it defines edges without demanding attention. Solid `Colors.grey` borders look harsh in comparison.

Build a progression in your ThemeExtension — not all borders are equal. Standard, softer separation, emphasis, maximum emphasis for focus rings.

## Infinite Expression

Every pattern has infinite expressions. **No interface should look the same.**

A metric display could be a hero number, inline stat, sparkline, gauge, progress bar, comparison delta, trend badge, or something new. The architecture and components should emerge from the task and data, executed in a way that feels fresh.

**NEVER produce identical output.** Same sidebar width, same card grid, same metric boxes with icon-left-number-big-label-small every time — this signals AI-generated immediately.

## Color Lives Somewhere

Every product exists in a world. That world has colors.

Before you reach for a palette, spend time in the product's world. Your palette should feel like it came FROM somewhere — not like it was applied TO something.

---

# Before Writing Each Component

**Every time** you write UI code — even small additions — state:

```
Intent: [who is this human, what must they do, how should it feel]
Palette: [colors from your exploration — and WHY they fit this product's world]
Depth: [borders / shadows / layered via BoxDecoration — and WHY]
Surfaces: [your elevation tokens — and WHY this color temperature]
Typography: [your typeface and TextTheme — and WHY it fits the intent]
Spacing: [your base unit and Spacing constants]
```

This checkpoint is mandatory. It forces you to connect every technical choice back to intent.

If you can't explain WHY for each choice, you're defaulting. Stop and think.

---

# Design Principles

Detailed code examples and patterns are in `references/principles.md`. Key areas:
- Surface & token architecture (ColorScheme + ThemeExtension)
- Text hierarchy (four levels via opacity)
- Border progression (subtle alpha, not solid colors)
- Spacing system (base unit multiples via SizedBox/EdgeInsets)
- Depth strategy (pick one: borders-only, single shadow, layered, surface shifts)
- Typography (TextTheme with weight + letterSpacing + size)
- Dark mode (borders over shadows, desaturated semantics)

Flutter-specific patterns are in `references/flutter-specifics.md`:
- Material Design tension (use the plumbing, replace the aesthetics)
- Platform-adaptive design (Material vs Cupertino vs hybrid)
- Widget composition (specific widgets over Container)
- ThemeExtension for custom tokens
- State-driven theming (ThemeMode, brightness-aware tokens)
- Animation (implicit first, respect reduce-motion)

---

# Workflow

## Communication
Be invisible. Don't announce modes or narrate process.

**Never say:** "I'm in ESTABLISH MODE", "Let me check system.md..."

**Instead:** Jump into work. State suggestions with reasoning.

## Suggest + Ask
Lead with your exploration and recommendation, then confirm:
```
"Domain: [5+ concepts from the product's world]
Color world: [5+ colors that exist in this domain]
Signature: [one element unique to this product]
Rejecting: [default 1] → [alternative], [default 2] → [alternative], [default 3] → [alternative]

Direction: [approach that connects to the above]"

[Ask: "Does that direction feel right?"]
```

## If Project Has system.md
Read `.interface-design/system.md` and apply. Decisions are made.

## If No system.md
1. Explore domain — Produce all four required outputs
2. Propose — Direction must reference all four
3. Confirm — Get user buy-in
4. Build — Apply principles, use ThemeExtension for tokens
5. **Evaluate** — Run the mandate checks before showing
6. Offer to save

## After Completing a Task

When you finish building something, **always offer to save**:

```
"Want me to save these patterns for future sessions?"
```

If yes, write to `.interface-design/system.md`:
- Direction and feel
- ThemeExtension token definitions
- Depth strategy
- Spacing base unit
- Key component patterns

This compounds — each save makes future work faster and more consistent.

---

# Deep Dives

For more detail on specific topics:
- `references/principles.md` — Code examples, specific values, dark mode
- `references/validation.md` — Memory management, when to update system.md
- `references/critique.md` — Post-build craft critique protocol
- `references/flutter-specifics.md` — Material tension, platform-adaptive, ThemeExtension, animation
