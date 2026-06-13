---
name: design-md
description: Author/validate/export Google's DESIGN.md token spec files.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [design, design-system, tokens, ui, accessibility, wcag, tailwind, dtcg, google]
    related_skills: [popular-web-designs, claude-design, excalidraw, architecture-diagram]
---

# DESIGN.md Skill

DESIGN.md is Google's open spec (Apache-2.0, `google-labs-code/design.md`) for
describing a visual identity to coding agents. One file combines:

- **YAML front matter** — machine-readable design tokens (normative values)
- **Markdown body** — human-readable rationale, organized into canonical sections

Tokens give exact values. Prose tells agents *why* those values exist and how to
apply them. The CLI (`npx @google/design.md`) lints structure + WCAG contrast,
diffs versions for regressions, and exports to Tailwind or W3C DTCG JSON.

## When to use this skill

- User asks for a DESIGN.md file, design tokens, or a design system spec
- User wants consistent UI/brand across multiple projects or tools
- User pastes an existing DESIGN.md and asks to lint, diff, export, or extend it
- User asks to port a style guide into a format agents can consume
- User wants contrast / WCAG accessibility validation on their color palette

For purely visual inspiration or layout examples, use `popular-web-designs`
instead. For *process and taste* when designing a one-off HTML artifact
from scratch (prototype, deck, landing page, component lab), use
`claude-design`. This skill is for the *formal spec file* itself.

## File anatomy

```md
---
version: alpha
name: Heritage
description: Architectural minimalism meets journalistic gravitas.
colors:
  primary: "#1A1C1E"
  secondary: "#6C7278"
  tertiary: "#B8422E"
  neutral: "#F7F5F2"
typography:
  h1:
    fontFamily: Public Sans
    fontSize: 3rem
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: "-0.02em"
  body-md:
    fontFamily: Public Sans
    fontSize: 1rem
rounded:
  sm: 4px
  md: 8px
  lg: 16px
spacing:
  sm: 8px
  md: 16px
  lg: 24px
components:
  button-primary:
    backgroundColor: "{colors.tertiary}"
    textColor: "#FFFFFF"
    rounded: "{rounded.sm}"
    padding: 12px
  button-primary-hover:
    backgroundColor: "{colors.primary}"
---

## Overview

Architectural Minimalism meets Journalistic Gravitas...

## Colors

- **Primary (#1A1C1E):** Deep ink for headlines and core text.
- **Tertiary (#B8422E):** "Boston Clay" — the sole driver for interaction.

## Typography

Public Sans for everything except small all-caps labels...

## Components

`button-primary` is the only high-emphasis action on a page...
```

## Token types

| Type | Format | Example |
|------|--------|---------|
| Color | `#` + hex (sRGB) | `"#1A1C1E"` |
| Dimension | number + unit (`px`, `em`, `rem`) | `48px`, `-0.02em` |
| Token reference | `{path.to.token}` | `{colors.primary}` |
| Typography | object with `fontFamily`, `fontSize`, `fontWeight`, `lineHeight`, `letterSpacing`, `fontFeature`, `fontVariation` | see above |

Component property whitelist: `backgroundColor`, `textColor`, `typography`,
`rounded`, `padding`, `size`, `height`, `width`. Variants (hover, active,
pressed) are **separate component entries** with related key names
(`button-primary-hover`), not nested.

## Canonical section order

Sections are optional, but present ones MUST appear in this order. Duplicate
headings reject the file.

1. Overview (alias: Brand & Style)
2. Colors
3. Typography
4. Layout (alias: Layout & Spacing)
5. Elevation & Depth (alias: Elevation)
6. Shapes
7. Components
8. Do's and Don'ts

Unknown sections are preserved, not errored. Unknown token names are accepted
if the value type is valid. Unknown component properties produce a warning.

## Workflow: authoring a new DESIGN.md

1. **Ask the user** (or infer) the brand tone, accent color, and typography
   direction. If they provided a site, image, or vibe, translate it to the
   token shape above.
2. **Write `DESIGN.md`** in their project root using `write_file`. Always
   include `name:` and `colors:`; other sections optional but encouraged.
3. **Use token references** (`{colors.primary}`) in the `components:` section
   instead of re-typing hex values. Keeps the palette single-source.
4. **Lint it** (see below). Fix any broken references or WCAG failures
   before returning.
5. **If the user has an existing project**, also write Tailwind or DTCG
   exports next to the file (`tailwind.theme.json`, `tokens.json`).

## Workflow: publishing to a design-token gallery

When the task is a recurring daily publishing job (gallery, archive, feed):

1. **Pull latest** to avoid conflicts: `git pull origin main`
2. **Study existing archive** for 2–3 past entries to avoid palette/theme collisions.
   If the last 3 systems were dark/bioluminescent, go warm or playful. Ensure
   each new system feels like a deliberate departure.
3. **Generate the DESIGN.md** per the authoring workflow above. Pick a vivid,
   evocative system name (not corporate). Include: 5–8 named colors, 3–4 type
   scales, 2–3 radius sizes, spacing scale, 2–3 component tokens.
4. **Create the dated directory**: `gallery/designs/YYYY-MM-DD/DESIGN.md`
5. **Write a minimal preview** `index.html` (hero + swatches + components) using
   the tokens. Link to the DESIGN.md and to the gallery root.
6. **Update the gallery index** (or equivalent feed file):
   - Replace the "today" entry with the new system
   - Push the previous today entry into the archive list
   - Preserve chronological order (newest first)
7. **Lint**, fix any AA contrast failures by darkening the accent (never by
   lightening the background, which breaks the palette metaphor).
   - If the ghost button (`backgroundColor: "transparent"`) triggers a false WCAG
     warning, ignore it — contrast against the page is page-dependent.
   - If unused palette colors trigger warnings, ignore them — palette color tokens
     are meant to be available, not all referenced by component tokens.
8. **git add -A, commit with system name, push** to `origin main`.

### Gallery index.html structure to maintain

```html
<!-- Today's highlight card (swatches, actions) -->
<div class="today-card">...</div>

<!-- Archive list (chronological) -->
<div class="months-grid">
  <div class="month-group">
    <h3>Month YYYY</h3>
    <div class="day-item">...</div>
  </div>
</div>
```

Both the "today" card and the archive entry must point to the same dated
subdirectory. Update both locations atomically — inconsistent links are a silent
deployment bug.

## Workflow: lint / diff / export

The CLI is `@google/design.md` (Node). Use `npx` — no global install needed.

```bash
# Validate structure + token references + WCAG contrast
npx -y @google/design.md lint DESIGN.md

# Compare two versions, fail on regression (exit 1 = regression)
npx -y @google/design.md diff DESIGN.md DESIGN-v2.md

# Export to Tailwind theme JSON
npx -y @google/design.md export --format tailwind DESIGN.md > tailwind.theme.json

# Export to W3C DTCG (Design Tokens Format Module) JSON
npx -y @google/design.md export --format dtcg DESIGN.md > tokens.json

# Print the spec itself — useful when injecting into an agent prompt
npx -y @google/design.md spec --rules-only --format json
```

All commands accept `-` for stdin. `lint` returns exit 1 on errors. Use the
`--format json` flag and parse the output if you need to report findings
structurally.

### Lint rule reference (what the 7 rules catch)

- `broken-ref` (error) — `{colors.missing}` points at a non-existent token
- `duplicate-section` (error) — same `## Heading` appears twice
- `invalid-color`, `invalid-dimension`, `invalid-typography` (error)
- `wcag-contrast` (warning/info) — component `textColor` vs `backgroundColor`
  ratio against WCAG AA (4.5:1) and AAA (7:1)
- `unknown-component-property` (warning) — outside the whitelist above

When the user cares about accessibility, call this out explicitly in your
summary — WCAG findings are the most load-bearing reason to use the CLI.

See `references/lint-findings.md` for session-accreted knowledge on false
positives, WCAG warm-tone recipes, and noisy output handling.
`scripts/wcag-probe.py` is a ready-to-run utility to binary-search a hex
color to WCAG AA/AAA pass thresholds against any background.

## Pitfalls

- **Don't nest component variants.** `button-primary.hover` is wrong;
  `button-primary-hover` as a sibling key is right.
- **Hex colors must be quoted strings.** YAML will otherwise choke on `#` or
  truncate values like `#1A1C1E` oddly.
- **Negative dimensions need quotes too.** `letterSpacing: -0.02em` parses as
  a YAML flow — write `letterSpacing: "-0.02em"`.
- **Section order is enforced.** If the user gives you prose in a random order,
  reorder it to match the canonical list before saving.
- **`version: alpha` is the current spec version** (as of Apr 2026). The spec
  is marked alpha — watch for breaking changes.
- **Token references resolve by dotted path.** `{colors.primary}` works;
  `{primary}` does not.
- **`colors.primary` should always be defined.** The linter warns (and downstream tools may guess) if `primary` is absent. Map it to your dominant text-fill color — typically the darkest on light themes, lightest on dark themes.
- **Ghost/transparent buttons trigger false WCAG warnings.** A `button-secondary` with
  `backgroundColor: "transparent"` gets flagged for low contrast. This is by design — contrast is page-dependent, not fill-dependent. No spec fix needed.
- **Warm accent colors on warm backgrounds often miss AA by a hair.** Terracotta tones at ~4.3:1 are common. Darken the accent slightly (e.g. `#B8501A` → `#A8461A`) rather than lightening the background — preserves the palette metaphor.
- **Bright saturated accents (magenta, cyan, forest) also miss AA on cream paper.** The fix is the same: darken the accent until AA passes. Use `scripts/wcag-probe.py` to binary-search the smallest darkening delta.
- **Publishing to a gallery: update BOTH the "today" card and the archive list.** Inconsistent links between the hero section and the archive list are a silent class of deployment bug. Change both in the same commit.
- **The CLI mixes npm engine warnings into stderr.** To inspect only validation results, redirect stderr: `2>/dev/null`.
- **When using `wcag-probe.py`, put the *background* color first, *text* color second.** The script treats `bg_hex` as the background and `start_hex` as the text/accent to darken or lighten. Reversing the arguments will suggest lightening the text when you meant to darken the background accent — opposite to the skill's recommended fix (darken the accent). Always run it as: `python wcag-probe.py <background> <accent> --target aa`.
- **Dark themes should avoid pure `#000000` and pure `#FFFFFF`.** Deep lacquer-black (`#0E0B0A`, `#050508`) paired with warm rice-paper white (`#F0EAE2`, `#E8DFD4`) reads as atmospheric rather than clinical. Pure contrasts feel like unstyled defaults; slightly tinted darks and warm lights give the palette a material identity.
- **Do not use `delegate_task` subagents for gallery publishing steps.** Both `gallery/index.html` and new `designs/YYYY-MM-DD/` files share the same Git working tree. Parallel subagent writes risk stale-file overwrites and double-commit races. Read existing files, design, patch, commit, and push directly in the main turn.

## Pencil.dev Interop (.pen files)

When the user's design workflow uses **Pencil.dev** (not just DESIGN.md HTML/CSS),
generate `.pen` JSON files alongside DESIGN.md specs. Pencil is a vector design
tool; its `.pen` format stores design systems as JSON with reusable components.

### Workflow: DESIGN.md → .pen library + page files

1. Create a `library/<name>.pen` file with:
   - Variables (colors, typography, spacing, radii) keyed as `$`-prefixed tokens
   - Reusable components marked `"reusable": true` (buttons, tags, cards)
   - Components follow: `"type": "frame"` with `"layout"` (flexbox-style)

2. Create `pages/<page-name>-{desktop,mobile}.pen` files that reference the library.
   **Critical:** Pencil refs require `{"type": "ref", "ref": "<component-id>"}`.
   Without refs, the library and pages are disconnected — changes to the library
   don't propagate to pages.

3. Handcrafted `.pen` files follow version `"2.11"` with structure:
   ```json
   {
     "version": "2.11",
     "name": "...",
     "variables": { "color.void": {"type":"color","value":"#050508"} },
     "children": [ { "id": "nav", "type": "frame", "layout": "horizontal", ... } ]
   }
   ```

4. Variables are referenced with `$` prefix: `"fill": "$color.void"`.

5. **Known limitation:** Hand-editing `.pen` JSON without Pencil desktop's import
   dialog means refs are fragile across files. Either merge library + pages into one
   document, or treat the library as a source-of-truth palette and pages as
   disposable layout templates that are refined in Pencil desktop.

### When to use .pen vs DESIGN.md

- **DESIGN.md** → For agents: machine-readable tokens, linting, CSS/Tailwind export.
- **.pen files** → For human designers: editable in Pencil desktop, native components,
  version-controllable JSON. Use as the bridge between agent-generated specs and
  human iteration.

## Spec source of truth

- DESIGN.md repo: https://github.com/google-labs-code/design.md (Apache-2.0)
- Pencil docs: https://docs.pencil.dev/ (private, user-provided)
- CLI: `@google/design.md` on npm
- License of generated DESIGN.md files: whatever the user's project uses;
  the spec itself is Apache-2.0.
