# Pencil CLI Reference

Pencil (`@pencil.dev/cli`) is a headless Node tool that generates editable `.pen` design files from AI prompts and MCP tools. It runs the same engine as the Pencil desktop/IDE app, no GUI required.

## Install

```bash
npm install -g @pencil.dev/cli
pencil version   # requires Node 18+
```

## Auth

- **Interactive:** `pencil login` (email+password or email+OTP) → token in `~/.pencil/session-cli.json`
- **Headless/CI:** `export PENCIL_CLI_KEY=pencil_cli_...` (Developer Keys in org settings)
- Check: `pencil status`

## Design Generation (Agent Mode)

```bash
# Create from prompt
pencil --out design.pen --prompt "Create a hero section with headline, subtitle, CTA button"

# Edit existing
pencil --in design.pen --out design-v2.pen --prompt "Add a sidebar nav"

# Specify model
pencil --out quick.pen --model claude-haiku-4-5 --prompt "Mobile hamburger menu"

# List models
pencil --list-models
```

Models: `claude-opus-4-6` (default, most capable), `claude-sonnet-4-6` (balanced), `claude-haiku-4-5` (fastest/cheapest)

## Export

```bash
pencil --in design.pen --export design.png --export-scale 2 --export-type png
# Types: png | jpeg | webp | pdf
```

## Batch Processing

```bash
pencil --tasks batch.json
```

`batch.json`:
```json
{
  "tasks": [
    { "out": "landing.pen", "prompt": "SaaS landing page with hero, features, pricing" },
    { "in": "app.pen", "out": "app-v2.pen", "prompt": "Add dark mode toggle" },
    { "out": "menu.pen", "model": "claude-haiku-4-5", "prompt": "Mobile hamburger menu" }
  ]
}
```

## Interactive Mode (MCP Tools)

```bash
pencil interactive -o output.pen           # headless
pencil interactive -i input.pen -o out.pen # headless edit
pencil interactive -a desktop -i my.pen    # connect to running app
```

Shell commands: `tool_name({ key: value })`, `save()`, `exit()`

Example:
```
pencil > get_editor_state({ include_schema: true })
pencil > batch_design({ operations: 'hero=I(document,{type:"frame",name:"Hero",...})' })
pencil > get_screenshot({ nodeId: "hero" })
pencil > save()
```

## MCP Tools Available

- **batch_design**: insert/update/delete/move/copy/replace nodes. G() for images: `G(nodeId,"ai",prompt)` AI image, `G(nodeId,"stock",keywords)` Unsplash
- **batch_get**: search/read by pattern or ID
- **get_screenshot**: screenshot of a node or full page
- **snapshot_layout**: structural view of the document
- **get_editor_state**: full document state with schema
- **get_variables / set_variables**: sync with CSS tokens (two-way)
- **export_nodes**: PNG/JPEG/WEBP/PDF export
- **get_guidelines**: access defined design guidelines

## CI/CD

```bash
export PENCIL_CLI_KEY=pencil_cli_...
export ANTHROPIC_API_KEY=sk-ant...
pencil --out onboarding.pen --prompt "3-step onboarding flow"
```

Envs: `PENCIL_CLI_KEY`, `ANTHROPIC_API_KEY`, `PENCIL_API_BASE` (default https://api.pencil.dev), `DEBUG`

## .pen Format (key points)

- JSON object tree. Each object: unique `id` (no `/`), `type` (rectangle, frame, text, ellipse, polygon, path, script, ref, group, note, etc.)
- Layout: top-level x/y = top-left; nested = relative to parent. Flexbox: `layout` ("none"|"vertical"|"horizontal"), `justifyContent`, `alignItems`, `gap`, `padding`
- SizingBehavior: "fit_content" | "fill_container"
- Graphics: `fill` (color/gradient/image/mesh_gradient), `stroke` (multiple fills), `effect` (blur/shadow). Multiple fills in document order.
- Components: mark `"reusable": true`. Instances via `{"type":"ref","ref":"<id>"}`. Overrides on ref, nested via `descendants` map.
- Slots: frame with `"slot": ["<reusable-child-ids>"]`.
- Variables: `"variables": { "color.bg": {"type":"color","value":"#FFF"} }`, referenced with `$` prefix: `"fill": "$color.bg"`. Themes: value arrays with `theme` keys; `themes` axis map.
- Document version: "2.11". Top-level: version, themes, imports, variables, children.

## Variables / Design Tokens

- "Create Pencil variables from my globals.css"
- "Update globals.css with these Pencil variables"
- DESIGN.md tokens map directly onto .pen variables (color/number/string types)

## Pitfalls

- No auto-save in GUI — save frequently, commit to Git
- Codex CLI: Pencil may modify/duplicate config.toml — back up before first use
- Figma image copy-paste not supported — import full Figma file or add images manually
- Scripts (Code on Canvas): sandboxed, synchronous, Math.random() deterministic, max 1000 nodes / 2s
- Windows: no standalone desktop app — use VS Code/Cursor extension
- Linux: X11 more stable than Wayland/Hyprland
