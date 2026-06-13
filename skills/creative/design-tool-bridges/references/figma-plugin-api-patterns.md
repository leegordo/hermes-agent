# Figma Plugin API — Common Patterns

Quick reference for frequent Plugin API operations when building bridge plugins.

## Node creation

```javascript
const frame = figma.createFrame();
frame.resize(1440, 800);
frame.x = 0;
frame.y = 0;
frame.name = 'Hero Section';
frame.fills = [{ type: 'SOLID', color: { r: 0.02, g: 0.02, b: 0.031 } }];

const rect = figma.createRectangle();
rect.resize(180, 48);
rect.cornerRadius = 8;
rect.fills = [{ type: 'SOLID', color: { r: 0, g: 0.941, b: 1 } }];

const ellipse = figma.createEllipse();
ellipse.resize(100, 100);

const line = figma.createLine();
line.resize(200, 0);
line.strokes = [{ type: 'SOLID', color: { r: 0.5, g: 0.5, b: 0.5 } }];
line.strokeWeight = 2;
```

## Text (requires async font loading)

```javascript
await figma.loadFontAsync({ family: 'Inter', style: 'Regular' });
const text = figma.createText();
text.fontName = { family: 'Inter', style: 'Regular' };
text.fontSize = 64;
text.characters = 'Headline';
text.fills = [{ type: 'SOLID', color: { r: 1, g: 1, b: 1 } }];
text.textAlignHorizontal = 'LEFT';
text.textAlignVertical = 'TOP';
text.lineHeight = { value: 72, unit: 'PIXELS' };
```

## Auto layout

```javascript
frame.layoutMode = 'VERTICAL';
frame.primaryAxisAlignItems = 'MIN';
frame.counterAxisAlignItems = 'CENTER';
frame.itemSpacing = 16;
frame.paddingTop = 24;
frame.paddingRight = 24;
frame.paddingBottom = 24;
frame.paddingLeft = 24;
```

## Effects (shadows)

```javascript
node.effects = [{
  type: 'DROP_SHADOW',
  color: { r: 0, g: 0, b: 0, a: 0.25 },
  offset: { x: 0, y: 4 },
  radius: 8,
  spread: 0,
  visible: true,
  blendMode: 'NORMAL'
}];
```

## UI communication

```javascript
figma.showUI(__html__, { width: 380, height: 520 });
figma.ui.onmessage = async (msg) => { /* ... */ };
figma.ui.postMessage({ type: 'success', message: 'Done!' });
```

## Selection and viewport

```javascript
figma.currentPage.selection = [node1, node2];
figma.viewport.scrollAndZoomIntoView([node1, node2]);
```
