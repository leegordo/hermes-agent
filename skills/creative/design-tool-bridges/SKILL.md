---
name: design-tool-bridges
description: "Bridge web/HTML prototypes into design tools (Figma, etc.) or generate native designs headlessly via Pencil CLI. Covers DOM-to-design-node conversion, plugin architecture, headless generation, and design-file handoff patterns."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [figma, design-tools, plugins, export, prototyping]
    related_skills: [claude-design, sketch, portfolio-website-redesign]
---

# Design Tool Bridges

Bridge web/HTML prototypes into design tools, or generate native editable design files headlessly.

## When to Use

- User generates a design in HTML/CSS (via DoodleHaus, Claude-design, v0, etc.) and wants it in Figma
- Headless server cannot access design tool APIs directly (OAuth blocked, REST API read-only)
- Need editable layers, not screenshots
- Building a design-generation tool that targets multiple output formats
- **VPS/agent needs to generate real, editable design files with no GUI or copy-paste**

## The Core Problem

Design tool APIs have asymmetric access:

| Tool | Read | Write | Headless? |
|------|------|-------|-----------|
| Figma REST API | Yes | Comments/vars only | PAT works |
| Figma Plugin API | Full | Full | Requires browser |
| Figma Official MCP | Full | Full | OAuth only, 403 headless |
| Figma Community MCP | Full | **None** | PAT works, but read-only |
| **Pencil CLI** | **Full** | **Full** | **Yes — standalone Node CLI** |

**Rule:** If you are on a headless VPS and need to *write* design files, **Pencil CLI is the right answer**. The Figma plugin bridge is a fallback for when the user specifically wants Figma-native layers and has a desktop browser.

## Recommended Hierarchy

| Use Case | Tool | Notes |
|----------|------|-------|
| **Headless generation on VPS** | Pencil CLI | Generates `.pen` files, editable in Pencil desktop/IDE |
| **User wants Figma specifically** | Custom Figma Plugin + JSON | Two-step paste workflow |
| **Desktop agent with OAuth** | Desktop Agent Relay | One-shot via Figma MCP |
| **Static reference only** | Screenshot | PNG via Playwright |

## Tool 1: Pencil CLI (Headless Generation)

Pencil (`@pencil.dev/cli`) is a standalone headless Node tool that generates editable `.pen` design files using AI prompts and MCP tools. It runs the same engine as the Pencil desktop/IDE app, no GUI required.

### Install
```bash
npm install -g @pencil.dev/cli
pencil version   # requires Node 18+
```

### Auth
- **Interactive:** `pencil login` (email+password or email+OTP) → token in `~/.pencil/session-cli.json`
- **Headless/CI:** `export PENCIL_CLI_KEY=pencil_cli_...` (created in org Settings → Developer Keys). Takes precedence over session token.
- Check: `pencil status`

### Generate a design
```bash
# Create from prompt
pencil --out design.pen --prompt "Create a hero section with headline, subtitle, CTA button"

# Edit existing
pencil --in design.pen --out design-v2.pen --prompt "Add a sidebar nav"

# Use a lighter model for speed
pencil --out quick.pen --model claude-haiku-4-5 --prompt "404 page illustration"
```

### Export to image
```bash
pencil --in design.pen --export hero.png --export-scale 2 --export-type png
# Types: png | jpeg | webp | pdf
```

### Batch processing
```bash
pencil --tasks batch.json
```
Where `batch.json`:
```json
{
  "tasks": [
    { "out": "landing.pen", "prompt": "SaaS landing page" },
    { "in": "app.pen", "out": "app-v2.pen", "prompt": "Dark mode" },
    { "out": "menu.pen", "model": "claude-haiku-4-5", "prompt": "Mobile menu" }
  ]
}
```

### Models
- `claude-opus-4-6` (default, most capable)
- `claude-sonnet-4-6` (balanced)
- `claude-haiku-4-5` (fastest/cheapest)
- List: `pencil --list-models`

### Keys: why this replaces the Figma bridge

| Before (Figma bridge) | After (Pencil) |
|----------------------|----------------|
| Generate HTML → convert to JSON → copy-paste → Figma plugin render | `pencil --out design.pen --prompt "..."` |
| Gradients drop, images become rectangles, fonts fall back to Inter | Native gradients, images, components, variables |
| Manual two-step workflow | Fully headless, automatable in cron/agent sessions |
| Non-version-control friendly | `.pen` is plain JSON, diffable, storable in Git |
| Locked to Figma ecosystem | Pencil .pen files are editable in VS Code/Cursor/desktop |

### Pencil CLI variables ↔ DESIGN.md tokens

Pencil variables map cleanly to DESIGN.md tokens:
- `"variables": { "color.bg": {"type":"color","value":"#FFF"} }`
- Referenced: `"fill": "$color.bg"`
- DESIGN.md `colors.primary` → Pencil `color.primary`

## Tool 2: Custom Figma Plugin + JSON Handoff

Use this when the user specifically needs Figma-native layers and has Figma Desktop.

**Architecture:**

A Figma plugin has three files:

```
manifest.json   # Plugin metadata + permissions
code.js         # Plugin runtime (node creation, font loading)
ui.html         # Plugin UI (paste JSON, show status)
```

### manifest.json

```json
{
  "name": "My Bridge",
  "id": "my-bridge",
  "api": "1.0.0",
  "main": "code.js",
  "ui": "ui.html",
  "editorType": ["figma"],
  "networkAccess": {
    "allowedDomains": ["*"],
    "devAllowedDomains": ["localhost:*", "127.0.0.1:*"]
  }
}
```

### code.js patterns

**Node creation:**
```javascript
const frame = figma.createFrame();
frame.resize(1440, 900);
frame.fills = [{ type: 'SOLID', color: { r: 0.02, g: 0.02, b: 0.03 } }];
```

**Font loading (required before creating text):**
```javascript
await figma.loadFontAsync({ family: 'Inter', style: 'Regular' });
const text = figma.createText();
text.fontName = { family: 'Inter', style: 'Regular' };
text.characters = 'Hello';
```

**Message passing between code.js and ui.html:**
```javascript
// In code.js
figma.showUI(__html__, { width: 380, height: 520 });
figma.ui.onmessage = async (msg) => {
  if (msg.type === 'render-json') {
    const data = JSON.parse(msg.json);
    // ... create nodes ...
    figma.ui.postMessage({ type: 'success', message: 'Done!' });
  }
};

// In ui.html
parent.postMessage({ pluginMessage: { type: 'render-json', json: '...' } }, '*');
window.onmessage = (event) => {
  const msg = event.data.pluginMessage;
  if (msg.type === 'success') { /* ... */ }
};
```

**Auto layout from flexbox:**
```javascript
frame.layoutMode = 'VERTICAL'; // or 'HORIZONTAL'
frame.primaryAxisAlignItems = 'MIN';   // flex-start → MIN, center → CENTER, space-between → SPACE_BETWEEN
frame.counterAxisAlignItems = 'CENTER';
frame.itemSpacing = 16;
frame.paddingTop = 24;
frame.paddingRight = 24;
frame.paddingBottom = 24;
frame.paddingLeft = 24;
```

## DOM-to-Design-JSON Conversion

The core technique: render HTML in a hidden iframe, read `getComputedStyle()`, and map CSS properties to design node properties.

**Key mappings:**

| CSS Property | Figma Property |
|-------------|----------------|
| `background-color` | `fills` (SOLID) |
| `color` | `fills` on TEXT |
| `font-size` | `fontSize` |
| `font-family` | `fontName.family` |
| `font-weight` | `fontName.style` (map 700→Bold, 600→Semi Bold, etc.) |
| `border-radius` | `cornerRadius` |
| `border` | `strokes` + `strokeWeight` |
| `box-shadow` | `effects` (DROP_SHADOW) |
| `opacity` | `opacity` |
| `display: flex` + `flex-direction` | `layoutMode` (VERTICAL/HORIZONTAL) |
| `gap` | `itemSpacing` |
| `padding-*` | `padding*` |
| `justify-content` | `primaryAxisAlignItems` |
| `align-items` | `counterAxisAlignItems` |

**Color parsing strategy:**
```javascript
function parseCssColor(colorStr) {
  if (!colorStr || colorStr === 'transparent') return null;
  const ctx = document.createElement('canvas').getContext('2d');
  ctx.fillStyle = colorStr;
  return ctx.fillStyle; // Always returns #rrggbb
}
```

**Box shadow parsing:**
```javascript
function parseBoxShadow(shadowStr) {
  const effects = [];
  const parts = shadowStr.split(/,(?![^\(]*\))/); // split on comma, not inside rgba()
  for (const part of parts) {
    const m = part.match(/([\d.-]+px)\s+([\d.-]+px)\s+([\d.-]+px)(?:\s+([\d.-]+px))?\s+rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)/);
    if (m) {
      effects.push({
        type: 'DROP_SHADOW',
        color: rgbToHex(+m[5], +m[6], +m[7]),
        opacity: m[7] !== undefined ? parseFloat(m[7]) : 1,
        offset: { x: parseFloat(m[1]), y: parseFloat(m[2]) },
        radius: parseFloat(m[3]),
        spread: m[4] ? parseFloat(m[4]) : 0
      });
    }
  }
  return effects;
}
```

**Text leaf detection:**
```javascript
const hasBlockChildren = Array.from(el.children).some(c => {
  const cs = window.getComputedStyle(c);
  return cs.display !== 'inline' && cs.display !== 'none';
});
const isTextLeaf = !hasBlockChildren && el.textContent.trim().length > 0 && el.children.length === 0;
```

## Limitations & Pitfalls

1. **Gradients:** CSS gradients do not map cleanly to Figma's gradient format. Convert to solid fills or implement gradient parsing separately.
2. **Images/SVGs:** Become plain rectangles. To support images, upload them to Figma first and create IMAGE fills.
3. **Transforms:** CSS transforms (rotate, scale, translate) are not reflected in bounding rects. Complex transforms need manual handling.
4. **Position drift:** Elements with `position: absolute` inside relative containers may have incorrect offsets. Use `getBoundingClientRect()` relative to a stable parent.
5. **Font availability:** Figma must have the font installed. Always fall back to Inter. Load fonts async before creating text nodes.
6. **Nested frames:** Body-wrapping frames should be unwrapped — the body itself should not become a frame, only its children.

### manifest.json pitfalls (real session fixes)

These Figma manifest validation errors were all caught in a single deployment session. Fix them before trying to load the plugin:

| Error | Fix |
|---|---|
| `Invalid value for networkAccess. If you want to allow all domains, please add a "reasoning" field` | Add `"reasoning": "The plugin fetches design JSON from external URLs and loads image assets."` inside the `networkAccess` object |
| `Invalid value for devAllowedDomains. 'localhost:*' must be a valid URL` | Use `"http://localhost"` not `"localhost:*"`. Figma requires full URLs, and rejects wildcard ports. Drop `127.0.0.1` entirely — it rejects IP addresses too |
| `The manifest editorType does not include "dev"` | Add `"dev"` to `editorType` array if the user is in Dev Mode: `["figma", "dev"]` |

**Minimal working `networkAccess` for wildcard access:**
```json
"networkAccess": {
  "allowedDomains": ["*"],
  "devAllowedDomains": ["http://localhost", "https://example.com"],
  "reasoning": "The plugin fetches design JSON from external URLs and loads image assets referenced in generated designs."
}
```

## Manifest Validation Quick Reference

When Figma rejects a manifest with cryptic errors, work through this checklist top-to-bottom — errors chain, so fixing one may reveal the next.

1. **Schema check**: Must be valid JSON. No trailing commas.
2. **`editorType`**: Must include `"figma"` for design mode. Must ALSO include `"dev"` for Dev Mode. Typical: `["figma", "dev"]`.
3. **`networkAccess.reasoning`**: Required if `allowedDomains` contains `"*"` (wildcard). Write a brief justification of why the plugin needs open domains.
4. **`networkAccess.devAllowedDomains`**: Must be **full URLs**, not bare hostnames. **No IP addresses** (`127.0.0.1` rejected even with protocol). **Do not use port wildcards** (`localhost:*` is invalid).

| Wrong | Right |
|---|---|
| `"localhost:*"` | `"http://localhost"` |
| `"127.0.0.1"` | `"http://localhost"` (drop IP entirely) |
| `"leegordo.github.io"` | `"https://leegordo.github.io"` |
| Missing `reasoning` | Add `reasoning` string |
| Only `"figma"` in `editorType` | Add `"dev"` if using Dev Mode |

## Installing a Development Plugin in Figma

1. Figma Desktop: **Plugins → Development → Import plugin from manifest**
2. Select `manifest.json`
3. Plugin appears under **Plugins → Development → [Plugin Name]**
4. After editing files, Figma auto-reloads the plugin (no restart needed for code.js/ui.html changes)

## References

- `references/figma-json-schema.md` — The JSON spec consumed by the plugin
- `references/figma-plugin-api-patterns.md` — Common Plugin API snippets (fonts, effects, constraints)
- `references/pencil-cli.md` — Pencil CLI install, auth, generation, export, and .pen format
- `references/manifest-validation-trail.md` — Real session transcript: 4-error manifest validation chain and fixes applied
- `templates/dom-to-figma-converter.js` — Reusable DOM parser that outputs Figma-compatible JSON
