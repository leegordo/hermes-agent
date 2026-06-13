# DoodleHaus → Figma JSON Schema v1

JSON format consumed by the DoodleHaus Bridge plugin.

## Top-level structure

```json
{
  "version": "1.0",
  "nodes": [
    { /* node */ },
    { /* node */ }
  ]
}
```

## Base node properties

| Property | Type | Description |
|----------|------|-------------|
| `type` | string | `FRAME`, `RECTANGLE`, `TEXT`, `ELLIPSE`, `LINE` |
| `name` | string | Layer name in Figma |
| `x` | number | X position in pixels |
| `y` | number | Y position in pixels |
| `width` | number | Width in pixels |
| `height` | number | Height in pixels |
| `fills` | array/object | Fill(s) — see Colors |
| `strokes` | array/object | Stroke fill(s) |
| `strokeWeight` | number | Stroke width |
| `strokeAlign` | string | `INSIDE`, `OUTSIDE`, `CENTER` |
| `cornerRadius` | number | Uniform corner radius |
| `topLeftRadius` | number | Individual corner overrides |
| `topRightRadius` | number | |
| `bottomLeftRadius` | number | |
| `bottomRightRadius` | number | |
| `opacity` | number | 0–1 |
| `effects` | array | Drop shadows — see Effects |
| `layoutMode` | string | `HORIZONTAL`, `VERTICAL` (auto layout) |
| `primaryAxisAlignItems` | string | `MIN`, `CENTER`, `MAX`, `SPACE_BETWEEN` |
| `counterAxisAlignItems` | string | `MIN`, `CENTER`, `MAX` |
| `itemSpacing` | number | Gap between children |
| `paddingTop` | number | |
| `paddingRight` | number | |
| `paddingBottom` | number | |
| `paddingLeft` | number | |
| `constraints` | object | `{ horizontal, vertical }` |
| `children` | array | Child nodes (recursive) |

## Colors

```json
// Hex string
{ "color": "#00f0ff" }

// RGB object (0–1 floats)
{ "color": { "r": 0, "g": 0.941, "b": 1 } }

// CSS rgb()
{ "color": "rgb(0, 240, 255)" }
```

## Fills

```json
// Solid
{ "type": "solid", "color": "#00f0ff", "opacity": 1 }

// Linear gradient
{
  "type": "gradient-linear",
  "gradientTransform": [[1,0,0],[0,1,0]],
  "gradientStops": [
    { "position": 0, "color": "#00f0ff", "opacity": 1 },
    { "position": 1, "color": "#a855f7", "opacity": 1 }
  ]
}
```

## Text nodes

| Property | Type | Description |
|----------|------|-------------|
| `characters` | string | Text content |
| `fontSize` | number | Font size in px |
| `fontName` | object | `{ family: "Inter", style: "Regular" }` |
| `textCase` | string | `ORIGINAL`, `UPPER`, `LOWER`, `TITLE` |
| `textDecoration` | string | `NONE`, `UNDERLINE`, `STRIKETHROUGH` |
| `letterSpacing` | number/object | Pixel value or `{ value, unit }` |
| `lineHeight` | number/object | Pixel value or `{ value, unit }` |
| `textAlignHorizontal` | string | `LEFT`, `CENTER`, `RIGHT`, `JUSTIFIED` |
| `textAlignVertical` | string | `TOP`, `CENTER`, `BOTTOM` |
| `color` | string/object | Shortcut for text fill color |

## Effects

```json
{
  "effects": [
    {
      "type": "DROP_SHADOW",
      "color": "#000000",
      "opacity": 0.25,
      "offset": { "x": 0, "y": 4 },
      "radius": 8,
      "spread": 0,
      "blendMode": "NORMAL"
    }
  ]
}
```
