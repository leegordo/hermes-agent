# Daily Design-Token Gallery Publishing — Playbook

Condensed operational guide for recurring daily publishing jobs that add a new
DESIGN.md system to a dated gallery, update a gallery index, and push.

## Pre-flight

1. `git pull origin main` before generating anything.
2. Inspect the last 2–3 dated entries to force a deliberate departure.
   - If all recent systems were dark → go warm, playful, or light editorial.
   - If recent used warm earthy ceramics → go cool, bioluminescent, or synthetic neon.
   - Avoid repeat adjectives ("dark", "warm", "minimal", "brutalist") for 2 days running.

## Theme invention rules

- Name must be vivid and evocative (one word or two), never corporate.
- Include: 5–8 named colors, 3–4 type scales, 2–3 radius sizes,
  spacing scale (≥ 4 stops), 2–3 component tokens (button, card, input).
- Dark theme: `primary` = light text, `asphalt` or `void` = deep background.
- Light theme: `primary` = dark text, `paper` or `cream` = background.
- Every accent color must pass WCAG AA (≥ 4.5:1) as text on its intended
  background. Run `wcag-probe.py <bg> <accent> --target aa` and darken until
  it passes — never lighten the background.

## File layout per day

```
gallery/designs/YYYY-MM-DD/
├── DESIGN.md     # Google DESIGN.md spec
└── index.html    # Minimal preview (hero + swatches + components)
```

The preview HTML must:
- Load exact Google Fonts named in the DESIGN.md `typography` tokens.
- Render a hero with system name, description, and tagline.
- Show all color swatches with name + hex.
- Render all typography scales with a sample line.
- Show components: button (primary + secondary), card, input/focus state.
- Link back to `DESIGN.md` and to the gallery root (`../../index.html`).
- Be a single self-contained HTML file (no external CSS dep besides fonts).

## Gallery index mutation rules

Two locations must be updated **atomically** (same commit):

1. **Today card** (hero section): replace badge date, title, description,
   swatch grid, and action links (`View System →`, `DESIGN.md`) to point at
   the new `designs/YYYY-MM-DD/` directory.
2. **Archive list** (month-group): push previous "today" entry into the archive
   stack at the top, preserving newest-first. Both `day-item` and today card
   must use identical URLs.

After editing, verify there are no stale URLs (e.g., remaining `designs/2026-06-06/`
in the today card while the swatches and links point to a different date).

## Commit & deploy

```bash
git add -A
git commit -m "{SystemName} — one-line description"
git push origin main
```

## Theme lineage examples (from 0xCreative archive)

| Date    | System          | Mood                | Palette        |
|---------|-----------------|---------------------|----------------|
| Jun 4   | Sablier         | Warm sand brutalism | `#F5EDD6` sand, ink, sienna |
| Jun 5   | Abyssal         | Bioluminescent deep | `#04090F` void, `#00F5D4` phosphor |
| Jun 6   | Halftone Fever  | Risograph zine      | `#F7F2E8` cream, `#C91A48` magenta |
| Jun 7   | Konshu          | Tokyo neon brutalism| `#0F0F17` asphalt, `#7733FF` violet |
| Jun 8   | Crépuscule      | Art-deco warm       | `#4A1942` purple, `#D4A017` gold |
| Jun 9   | Isfjord         | Nordic ice minimal  | `#EDF2F7` ice, `#4B7991` glacier |
| Jun 10  | Tessera         | Mediterranean warm  | `#F5EFE4` parchment, `#AB5527` terra |
| Jun 11  | Vellum          | Archival manuscript | `#F0EADE` vellum, `#A03030` vermillion |
| Jun 12  | Cinnabar        | East Asian lacquer  | `#0E0B0A` lacquer, `#BE3D2D` cinnabar |
| Jun 13  | Gelato          | Memphis pastel joy  | `#FDF6F0` cream, `#DC1C51` sorbet, `#4E5FBE` periwinkle |

Pattern: no mood, hue family, or lightness regime repeats for >1 entry.

## Lint expectations (zero errors target)

The `npx @google/design.md lint` command typically produces 0 errors but **may**
emit warnings that are safe to ignore for this gallery workflow:

- **Ghost button** (`backgroundColor: "transparent"`) — WCAG warning is false
  positive; contrast is page-dependent, not fill-dependent.
- **Unused palette colors** (e.g. `pistachio` defined but not referenced by any
  `components:` token) — palette colors are intentionally comprehensive. Do not
  strip them to silence warnings; component coverage is not the same as palette
  coverage.
- **Stderr noise** (`npm WARN engine`, deprecation notices) — suppress with
  `2>/dev/null` when parsing JSON output.

Only actual `broken-ref`, `duplicate-section`, `invalid-*`, and
`wcag-contrast` on opaque component fills should trigger real fixes.
