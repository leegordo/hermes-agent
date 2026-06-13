---
name: portfolio-website-redesign
description: "Full visual redesign workflow for portfolio or marketing websites. From concept generation → static mockup review → production codebase implementation. Covers Next.js + Tailwind sites specifically."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [portfolio, website, redesign, nextjs, tailwind, visual-design, mockup]
    related_skills: [sketch, remote-static-preview, subagent-driven-development]
---

# Portfolio / Website Redesign

## Overview

When a user wants to visually redesign their portfolio or marketing site, follow this phased workflow. Never jump straight into editing the production codebase — always validate the visual direction with static mockups first.

**This workflow assumes:** Next.js + Tailwind CSS codebase (the modern default for portfolio sites). Adapt font loading and config files for other stacks.

## Phase 1: Concept Generation (Parallel)

Generate 2–3 visually distinct static HTML mockups. Use `delegate_task` with subagents to work in parallel — each subagent produces one complete `index.html` with inline CSS.

### Direction Briefing for Subagents

Each subagent needs:
- **Brand constraints:** Logo (base64-embedded), any sacred brand elements, colors to avoid
- **Content:** Real copy from the existing site (hero text, services, testimonials, projects)
- **Typography:** Google Fonts or system fonts (no external dependencies beyond fonts)
- **Anti-patterns:** Explicitly forbid AI-template slop (dark mode + gradients + Geist + card grids) unless requested

**Critical:** Base64-embed the logo so mockups work offline:
```bash
python3 -c "import base64; print(f'data:image/png;base64,{base64.b64encode(open(\"logo.png\",\"rb\").read()).decode()}')"
```

### Logo Usage Rule

The user's logo is usually their most personal design artifact. Unless they explicitly say otherwise:
- **Use it once:** navigation header only
- **Never use it as:** background watermark, footer decoration, hero filler, repeated pattern
- If they spent significant time designing it, they will notice misuse and be annoyed

### Restyling Existing HTML Documents to Match the Brand System

When a user asks you to restyle an existing HTML file (PRD, doc, landing page) to match their portfolio design system, use a systematic bulk-replace approach rather than hand-editing.

**Token mapping (this user's palette):**

| Role | Light-theme source | Dark-theme target |
|------|-------------------|-------------------|
| Page background | `#F1F2F2` | `#0c0c10` |
| Card background | `#FCFCFC` | `#141418` |
| Section background | `#F9F9F9` | `#1a1a1f` |
| Subtle background | `#F5F5F5` | `#1f1f24` |
| Border | `#E5E5E5` | `#2a2a30` |
| Border strong | `#A3A3A3` | `#4a4a50` |
| Body text | `#4D4D4F` | `#6a6a70` |
| Heading text | `#373739` | `#f0f0f5` |
| Muted text | `#737373` | `#6a6a70` |
| Brand / accent | `#BB3526` | `#e85a8a` |
| Brand hover | `#C2493C` | `#f0709a` |
| Secondary accent | `#3A6682` | `#8a9ab0` |
| Success | `#16A34A` | `#4ade80` |
| Error | `#DC2626` | `#f87171` |
| Code block bg | `#1f1f21` | `#0a0a0e` |
| Code block text | `#f1f2f2` | `#e8e8ec` *(protected)* |
| Inline code bg | `#F2F2F2` | `#1a1a1f` |
| Success bg tint | `#F0FDF4` | `rgba(74,222,128,0.08)` |
| Success border | `#BBE5C8` | `rgba(74,222,128,0.25)` |

**Font mapping:**
- Sans/Display: `Inter` / `Encode Sans Condensed` → `Space Grotesk`
- Mono: `ui-monospace` → `JetBrains Mono`
- Update both CSS `font-family` declarations AND SVG `font-family` attributes.

**Critical pitfall — protect text-on-color colors:**
Some source colors serve double duty. `#f1f2f2` may be the page background AND the text color inside `pre` blocks or on colored SVG rectangles. A naive global replace will turn code text invisible (dark-on-dark) or break SVG labels.

**Fix:** Pre-protect before bulk replacement:
```python
# 1. Protect colors that are text-on-background before replacing backgrounds
content = content.replace('color: #f1f2f2;', 'color: #PRE_TEXT;')

# 2. Do all bulk replacements
content = content.replace('#F1F2F2', '#0c0c10')  # now safe
# ... etc for every mapping

# 3. Restore protected colors
content = content.replace('#PRE_TEXT', '#e8e8ec')
```

Also protect `#FAFAFA` text on colored SVG rectangles — these usually stay light against dark-themed accent boxes.

**Logo embedding:** If the document has a masthead or header, insert the user's logo as an `<img>` pointing to `https://leegordon.design/images/logo.png` with `width="40" height="40"` and `opacity:0.9`.

**Add Google Fonts:** Insert preconnect + stylesheet links for `Space Grotesk` and `JetBrains Mono` before `</head>`.

### Contrast & Readability Pitfalls

When a user says a design direction is "too intense" or text is "hard to read":
1. **Body text contrast:** Bump from `#5c5c75`-level to `#a0a0b8` or higher. Users need comfortable long-form reading.
2. **Accent saturation:** Neon magenta (`#ff1a75`) → softer rose (`#e85a8a`). Remove glow/shadow effects on text.
3. **CTA loudness:** Filled bright pills → outline buttons with subtle hover tint. No background color inversion on hover.
4. **Muted text hierarchy:** Ensure at least 3 readable tiers: body `#a0a0b8`, secondary `#6a6a85`, decorative `#4a4a60`.

Always test: body text at 0.95rem should be readable at normal viewing distance without strain.

### Step 2: Host for Review

Serve the mockups from the VPS so the user can view them remotely. Use the `remote-static-preview` skill.

**Critical VPS setup — verify remote accessibility:**
```bash
# 1. Get the VPS public IP (NOT 127.0.0.1)
curl -s icanhazip.com

# 2. Serve on ALL interfaces (0.0.0.0), NOT localhost (127.0.0.1)
python3 -m http.server 8001 --bind 0.0.0.0

# 3. Open firewall ports
ufw allow 8001/tcp && ufw allow 8002/tcp && ufw allow 8003/tcp

# 4. Verify listening on public interface
ss -tlnp | grep -E "800[123]"
# Should show 0.0.0.0:8001, NOT 127.0.0.1:8001

# 5. Smoke-test from the VPS itself
curl -s -o /dev/null -w "%{http_code}" http://<PUBLIC_IP>:8001/
```

**Common failure:** Serving on `127.0.0.1` (the default) makes the preview localhost-only. The user cannot reach it from Costa Rica (or anywhere outside the VPS). Always use `--bind 0.0.0.0`.

Present all URLs together with one-sentence descriptions of each direction.

## Phase 3: Iterate on Feedback

When the user picks a direction, they will have refinements. Common requests:

| Request | Typical Fix |
|---------|-------------|
| "Too intense / hard to read" | Raise body text contrast (#5c5c75 → #a0a0b8), tone down accent saturation |
| "Logo is everywhere" | Remove from hero, footer, backgrounds — keep nav only |
| "CTA is too loud" | Switch from filled pill to outline button, remove glow/shadow |
| "Not differentiated enough" | Push type scale further, add asymmetric layouts, break the grid |

Rewrite the chosen mockup's HTML and re-serve on the same port. Do not edit the production codebase yet.

## Phase 4: Port to Production Codebase

Once the mockup is approved, implement it in the real Next.js app.

### Step 1: Audit the Codebase

Read these files in order:
1. `tailwind.config.ts` — color palette, font families, spacing scale
2. `app/layout.tsx` — root layout, font imports, metadata
3. `styles/globals.css` — CSS variables, base styles, utility classes
4. `app/page.tsx` — home page composition
5. Key components: `Navigation.tsx`, `Footer.tsx`, `Hero.tsx`, `ProjectGrid.tsx`, etc.
6. `lib/content.ts` — data layer (do NOT break this)

### Step 2: Update Global Styles

1. **Tailwind config:** Update colors, fonts, font sizes. Add new color tokens (e.g., `accent`, `body`, `muted`).
2. **Layout:** Swap font imports (e.g., Geist → Space_Grotesk + JetBrains_Mono from `next/font/google`).
3. **Globals CSS:** Update CSS variables to match new palette.

### Step 3: Update Components

Work top to bottom:
1. `Navigation.tsx` — simplify if needed, update colors
2. `Hero.tsx` — new layout, typography, CTA style
3. `page.tsx` sections — trust bar, services, testimonials, pricing
4. `ProjectGrid.tsx` / `ProjectCard.tsx` — new card layout (e.g., alternating full-bleed rows)
5. `Footer.tsx` — simplified if appropriate

**Preserve the data layer:** Keep `lib/content.ts`, MDX files, and JSON content files intact. Only change presentation.

### Step 4: Build & Verify

```bash
npm run build
```

Fix any TypeScript or build errors before committing.

### Step 5: Commit & Push

```bash
git add -A
git commit -m "Visual redesign: <direction name>

- New color palette: <brief>
- New typography: <fonts>
- <key layout changes>"
git push origin main
```

If push fails (no auth), ask the user for a PAT or use HTTPS with token in URL.

## Color Palette Reference (Direction 3 Example)

When the user wants a bold conceptual direction that remains readable (not neon/intense):

See full production reference: `references/direction-3-bold-example.md`

Key tokens:
```css
--bg: #0c0c10;
--text-body: #a0a0b8;      /* readable body copy */
--text-muted: #6a6a85;      /* secondary text */
--text-faint: #4a4a60;      /* labels, decorative */
--accent: #e85a8a;          /* rose, not neon magenta */
--accent-soft: #f080a0;     /* hover states */
--accent-muted: rgba(232, 90, 138, 0.12);
--border: rgba(232, 232, 240, 0.08);
```

## Typography Reference

```typescript
// next/font/google
import { Space_Grotesk, JetBrains_Mono } from "next/font/google";

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-space-grotesk",
  weight: ["300", "400", "500", "600", "700"],
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains-mono",
  weight: ["400", "500"],
});
```

Tailwind config:
```typescript
fontFamily: {
  sans: ["var(--font-space-grotesk)", "system-ui", "sans-serif"],
  display: ["var(--font-space-grotesk)", "system-ui", "sans-serif"],
  mono: ["var(--font-jetbrains-mono)", "monospace"],
},
```

## Key Principles

1. **Mockup first, codebase second.** Never redesign the production site without user approval of a static mockup.
2. **Parallel directions.** Generate 2–3 genuinely distinct directions, not variations of the same idea.
3. **Embed assets.** Base64-embed logos/images so mockups have zero external dependencies.
4. **Preserve content.** The data layer (`lib/content.ts`, MDX, JSON) stays untouched — only presentation changes.
5. **Build clean.** Always `npm run build` before committing. Fix TS errors immediately.
6. **One commit per redesign phase.** Squash the implementation into a single descriptive commit.
