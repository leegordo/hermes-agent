# AI Prompt Tool — 3-Zone Layout Pattern

Reference: neuform.ai, v0.dev, Lovable, Google Stitch, and similar AI design-generation tools.

## The Pattern

A three-zone layout optimized for prompt-to-artifact workflows:

```
+--------------------------------------------------+
| LEFT SIDEBAR    |      CENTER CANVAS              |
| (~180px, dark)  |      (flexible, dark grain)     |
|                 |                                 |
| - Logo          |      - Preview viewport         |
| - Nav tabs      |      - Resize handles           |
| - Search        |      - Error/success states     |
| - Feed/Gallery  |                                 |
| - Projects      |                                 |
| - CTA button    |                                 |
+-----------------+---------------------------------+
| BOTTOM PROMPT BAR (floating, full-width)         |
| - Prompt textarea                                |
| - Type selector modal (Hero, Features, Pricing,  |
|   Login, Mobile, Footer, Section, etc.)          |
| - Model selector modal                           |
| - Tool icons (globe, history, pages, layers,     |
|   link, image, grid)                             |
| - Create button (blue, prominent)                |
| - PRO TIP toast                                  |
| - 60 FPS indicator                               |
+--------------------------------------------------+
```

## Zone Details

### Left Sidebar
- **Background:** Near-black charcoal (#0f0f0f to #1a1a1a)
- **Width:** ~180px, fixed
- **Elements:**
  - Logo/sparkle icon + external link icon at top
  - Navigation tabs: HOME / GALLERY / SKILLS (or similar)
  - Search bar with magnifying glass
  - Feed section: Featured, Pro, Trending, Upcoming, Favorites
  - Tags section: Animated, WebGL, ThreeJS, Effect, Bento, Section, Charts, CTA, Dashboard, Dither
  - Top Creators section (collapsible)
  - Bottom: utility icons + "Start trial" gradient button

### Center Canvas
- **Background:** Very dark with subtle grain/noise texture
- **Border:** Thin reddish-orange or subtle outline when active
- **Content:**
  - Floating preview cards with resize handles
  - Error states (dark burgundy card: "GENERATION FAILED" + file path + regenerate button)
  - Success states (rendered HTML preview)
  - Notification banners at top (red/maroon for errors, yellow for tips)

### Bottom Prompt Bar
- **Position:** Fixed to bottom, floating above edge
- **Background:** Dark charcoal with rounded corners
- **Elements:**
  - **PRO TIP toast** (yellow/amber, dismissible): "Drag and drop a design screenshot to get the best results."
  - **Prompt textarea:** Large input with monospace-style text
  - **Type selector:** Dropdown modal with icons — Default, Instagram Slide, Slide Deck, Branding, Mobile, Login, Hero, Features, Pricing, FAQ, Testimonials, Footer, Section, Background, SVG, WebGL, ThreeJS, Animation, Motion Design
  - **Model selector:** Gemini 3.1 Pro, GPT-5.5, Claude Opus, etc. with 2X/PRO badges
  - **Tool icons:** Globe, history/clock, pages (with badge), layers, link, image, grid, text formatting
  - **Create button:** Blue, rounded, prominent
  - **Expand button:** Fullscreen toggle
  - **60 FPS indicator:** Bottom-right corner

## Key Modals

### Type Selector
- Title: "Type"
- Subtitle: "Choose the output format for this create prompt."
- Options with left-aligned icons:
  - Default (grid icon, "CURRENT" badge)
  - Instagram Slide (camera icon)
  - Slide Deck (monitor icon)
  - Branding (sparkle icon)
  - Mobile (phone icon)
  - Login (arrow icon)
  - Hero (star icon)
  - Features (layout icon)
  - Pricing (tag icon)
  - FAQ (question icon)
  - Testimonials (quote icon)
  - Footer (document icon)
  - Section (lines icon)
  - Background (image icon)
  - SVG (pen icon)
  - WebGL (bolt icon)
  - ThreeJS (cube icon)
  - Animation (play icon)
  - Motion Design (wave icon)

### Model Selector
- Title: "Model"
- Subtitle: "Pick the model for this prompt."
- Options with capability badges:
  - Gemini 3.1 Pro ("CURRENT" badge)
  - Gemini 3.5 Flash
  - Gemini 3 Flash
  - OpenAI GPT-5.5 ("2X" badge)
  - Claude Opus 4.8 ("2X" + "PRO" badges)
  - Kimi K2.5
  - Kimi K2.6

### Import from Figma
- Title: "Import from Figma"
- Description: "Paste a Copy link to selection URL to attach node data as a prompt file."
- Fields:
  - FIGMA URL: `https://www.figma.com/design/...&node-id=...`
  - FIGMA API TOKEN: with "Get token" link and eye toggle
- Helper text: "Add a selection link and token to preview the node before importing."
- Buttons: Cancel (gray), Import (blue)

### Pricing / Upgrade
- Title: "Production Runway" or similar
- Headline: "Keep creating and ship the result."
- Subheadline: Trial details and feature list
- Trust bar: User count, Google recommendation, trusted-by logos
- Billing toggle: Monthly / Annual
- Pricing cards (4 columns):
  - Free ($0/mo, no generation)
  - Pro ($25/mo, 200 prompts, highlighted with gradient)
  - Max ($50/mo, 500 prompts)
  - Ultra ($100/mo, 1200 prompts)
- Bottom action bar with "Start Pro Trial" button

## Color Palette
- **Backgrounds:** #0a0a0a to #1a1a1a (near-black charcoal)
- **Surface:** #1e1e1e to #2d2d2d (elevated panels)
- **Text primary:** #ffffff (white)
- **Text secondary:** #a0a0a0 (light gray)
- **Text muted:** #555555 (dark gray)
- **Accent:** #3b82f6 (blue) or #6366f1 (indigo)
- **Accent gradient:** Blue-to-purple for highlighted cards
- **Success:** #22c55e (green)
- **Warning:** #f59e0b (amber)
- **Error:** #ef4444 (red) / #7f1d1d (dark red for error cards)
- **PRO TIP:** #fbbf24 (yellow-amber)

## Typography
- **Primary:** Inter or similar geometric sans-serif
- **Mono:** JetBrains Mono or similar for code/paths
- **Scale:** Small labels (0.7rem), body (0.9rem), headings (1.1-1.5rem), prices (2-3rem)

## User Preference: No Community/Social Features

When building this pattern for a personal workspace (not a community platform):
- **DO NOT** add social features: likes, comments, followers, public profiles
- **DO NOT** frame the feed as "community" — it's a personal gallery of agent-generated work
- **DO** structure the feed as: agent-generated examples, daily outputs, project history
- **DO** focus on: personal project workspace, monetization (pricing tiers), private generation
- **DO** use language like "Your projects", "Agent gallery", "Generated examples" not "Community", "Feed", "Social"

## Implementation Notes

- Use CSS Grid for the main layout: `grid-template-columns: 180px 1fr`
- Use `position: fixed` for the bottom prompt bar
- Use `backdrop-filter: blur()` for floating panels
- Add grain/noise texture to canvas background via SVG filter or CSS
- Implement modals with pure CSS/JS (no external libraries)
- Use `localStorage` for: auth state, project list, prompt history, selected model
- The prompt bar should be functional: on Create, show loading state, then render output in canvas
