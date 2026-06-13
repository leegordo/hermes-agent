# Direction 3: Bold Conceptual — Production Palette Reference

Production-tested color palette for a bold, conceptual portfolio website.
Dark background with rose accent. Emphasizes readability over intensity.

## CSS Variables

```css
:root {
  --bg: #0c0c10;
  --bg-elevated: #14141c;
  --surface: #1a1a22;
  --surface-light: #22222c;

  --text: #e8e8f0;
  --text-body: #a0a0b8;      /* primary body copy */
  --text-muted: #6a6a85;      /* secondary text, nav links */
  --text-faint: #4a4a60;      /* labels, decorative text */

  --accent: #e85a8a;          /* rose — softer than neon magenta */
  --accent-soft: #f080a0;     /* hover states, emphasis */
  --accent-muted: rgba(232, 90, 138, 0.12);

  --border: rgba(232, 232, 240, 0.08);
  --border-hover: rgba(232, 232, 240, 0.15);
}
```

## Typography

- **Primary display:** Space Grotesk (Google Fonts) — weights 300-700
- **Monospace labels:** JetBrains Mono (Google Fonts) — weights 400-500
- Font sizes use `clamp()` for fluid scaling:
  - Hero: `clamp(4rem, 16vw, 14rem)` — line-height 0.88, tracking -0.04em
  - Section titles: `clamp(2.5rem, 7vw, 5.5rem)` — line-height 0.95, tracking -0.03em

## Key Design Decisions

### Navigation
- Logo appears only in the nav header — nowhere else on the page
- Links: Work, Services, Approach, Get in touch
- Get in touch uses accent color; others use muted gray

### Hero
- Massive name: "Lee" (white) + "Gordon." (rose accent)
- Bottom-aligned, not center-aligned
- Single outline CTA, not dual buttons
- CTA text: "See how I work →"

### Trust Bar
- Horizontal strip between hero and services
- Monospace "Trusted by" label in faint color
- Client names in muted gray, spaced generously

### Services Grid
- 3-column, border-collapsed grid
- Each card has: monospace number (01/02/03), bold title, light body copy
- Hover: subtle accent border tint, subtle accent background tint
- No card backgrounds — flat grid lines define the structure

### Projects
- Alternating layout: image left/text right, then reversed
- Full-width cards with tight border between them
- Image: opacity 40%, hover to 60%, subtle pink scan-line overlay
- Meta line in monospace: "Client — Year — Role"
- Metric badge: monospace, accent border, subtle background

### Testimonials
- 3-column cards with gradient top border (accent → transparent)
- Metric label in monospace accent above the quote
- Quote text in body color, lighter weight
- Name in white, title in muted

### Pricing
- 3-column cards with top accent line on hover
- Price in large bold accent
- /mo suffix in muted, normal weight
- Tier labels in monospace uppercase

### Footer
- No logo (per user request)
- Single-row: bio text + social links
- Social links hover to accent color

## What Changed from v1 → v2

**v1 (too intense):**
- Body text `#5c5c75` — unreadable
- Accent `#ff1a75` — neon, harsh
- Text-shadow glow on hero title
- Filled CTA with bright background
- Logo as hero watermark, footer, nav

**v2 (approved):**
- Body text `#a0a0b8` — comfortable reading
- Accent `#e85a8a` — rose, softer
- No glow effects
- Outline CTA, subtle hover tint
- Logo in nav only
