# Pencil.dev Quick Reference

Pencil is a vector design tool with deep AI integration via MCP. Designs are
stored as `.pen` JSON files (version 2.11).

## Key Principles

- **`.pen` = JSON object tree**: Each node has `"id"`, `"type"`, and layout props.
  Types: `frame`, `rectangle`, `text`, `ellipse`, `polygon`, `path`, `group`,
  `ref` (component instance), `script`, `note`.

- **Layout**: Flexbox-style. `layout` = `"none" | "vertical" | "horizontal"`.
  `justifyContent`, `alignItems`, `gap`, `padding`.
  Sizing: `"fit_content"` or `"fill_container"`.

- **Variables (Tokens)**: `"variables": { "color.void": {"type":"color","value":"#050508"} }`
  Reference with `$`: `"fill": "$color.void"`.

- **Components**: Mark `"reusable": true`. Instantiate via `{"type":"ref","ref":"<id>"}`.
  Overrides: set props on the ref. Variants are separate components, not nested.

- **Slots**: Frame with `"slot": ["<reusable-child-ids>"]`.

- **Themes**: `themes` axis map on document. Child `"theme"` prop applies downward.

## CLI (when authenticated)

`npm install -g @pencil.dev/cli`

```bash
pencil --out design.pen --prompt "Create a login page with..."
pencil --in design.pen --export design.png --export-scale 2
pencil interactive -o output.pen  # MCP tools direct
pencil --tasks batch.json         # batch process
```

Models: `claude-opus-4-6` (default), `claude-sonnet-4-6`, `claude-haiku-4-5`.

## Auth Options

1. **Interactive**: `pencil login` (email+OTP)
2. **CI/CD**: `PENCIL_CLI_KEY=pencil_cli_...` (org Developer Keys)

Headless auth requires the CLI key — desktop app session does not automatically
authorize the CLI tool.

## Link with DESIGN.md

DESIGN.md tokens map *cleanly* onto `.pen` variables (color/number/string types).
Workflow: DESIGN.md spec as source-of-truth for tokens → `.pen` library for
reusable components → page files using refs. See SKILL.md for page generation
guidance.

## Full docs

User's consolidated copy: `~/Projects/pencil-docs.md` on VPS (source:
https://docs.pencil.dev/ — private repo).
