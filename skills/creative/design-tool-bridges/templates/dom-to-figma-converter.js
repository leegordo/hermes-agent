/**
 * DOM-to-Figma JSON Converter
 * Parses computed styles from a rendered HTML element tree and outputs
 * Figma-compatible structured JSON.
 *
 * Usage:
 *   const json = domToFigmaJSON(document.body);
 *   // json = { version: '1.0', nodes: [...] }
 */

function rgbToHex(r, g, b) {
  return '#' + [r, g, b].map(x => {
    const hex = Math.round(x).toString(16);
    return hex.length === 1 ? '0' + hex : hex;
  }).join('');
}

function parseCssColor(colorStr) {
  if (!colorStr || colorStr === 'rgba(0, 0, 0, 0)' || colorStr === 'transparent') return null;
  const ctx = document.createElement('canvas').getContext('2d');
  ctx.fillStyle = colorStr;
  const computed = ctx.fillStyle;
  if (computed.startsWith('#')) return computed;
  const m = computed.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)/);
  if (m) return rgbToHex(+m[1], +m[2], +m[3]);
  return null;
}

function parseBoxShadow(shadowStr) {
  if (!shadowStr || shadowStr === 'none') return [];
  const effects = [];
  const parts = shadowStr.split(/,(?![^\(]*\))/);
  for (const part of parts) {
    const inset = part.includes('inset');
    if (inset) continue;
    const m = part.match(/([\d.-]+px)\s+([\d.-]+px)\s+([\d.-]+px)(?:\s+([\d.-]+px))?\s+rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)/);
    if (m) {
      effects.push({
        type: 'DROP_SHADOW',
        color: rgbToHex(+m[5], +m[6], +m[7]),
        opacity: m[7] !== undefined ? parseFloat(m[7]) : 1,
        offset: { x: parseFloat(m[1]), y: parseFloat(m[2]) },
        radius: parseFloat(m[3]),
        spread: m[4] ? parseFloat(m[4]) : 0,
        blendMode: 'NORMAL'
      });
    }
  }
  return effects;
}

function getFontStyle(weight) {
  const w = parseInt(weight);
  if (w >= 700) return 'Bold';
  if (w >= 600) return 'Semi Bold';
  if (w >= 500) return 'Medium';
  if (w >= 300) return 'Light';
  return 'Regular';
}

function domToFigmaNodes(el, parentRect) {
  const nodes = [];
  const rect = el.getBoundingClientRect();
  const style = window.getComputedStyle(el);

  if (style.display === 'none' || style.visibility === 'hidden') return nodes;
  if (rect.width < 1 || rect.height < 1) return nodes;
  if (['SCRIPT','STYLE','HEAD','META','LINK','NOSCRIPT'].includes(el.tagName)) return nodes;

  const x = rect.left - parentRect.left;
  const y = rect.top - parentRect.top;

  const hasBlockChildren = Array.from(el.children).some(c => {
    const cs = window.getComputedStyle(c);
    return cs.display !== 'inline' && cs.display !== 'none';
  });

  const textContent = el.textContent.trim();
  const isTextLeaf = !hasBlockChildren && textContent.length > 0 && el.children.length === 0;

  if (isTextLeaf) {
    const fontSize = parseFloat(style.fontSize);
    const color = parseCssColor(style.color);
    const fontFamily = style.fontFamily.split(',')[0].replace(/["']/g, '').trim();
    const fontWeight = style.fontWeight;
    const textAlign = style.textAlign;

    const textNode = {
      type: 'TEXT',
      name: el.tagName.toLowerCase() + (el.id ? '-' + el.id : ''),
      x: Math.round(x),
      y: Math.round(y),
      width: Math.round(rect.width),
      height: Math.round(rect.height),
      characters: textContent,
      fontSize: fontSize,
      fontName: { family: fontFamily || 'Inter', style: getFontStyle(fontWeight) },
      textAlignHorizontal: textAlign === 'center' ? 'CENTER' : textAlign === 'right' ? 'RIGHT' : 'LEFT',
      textAlignVertical: 'TOP',
      lineHeight: { value: fontSize * 1.4, unit: 'PIXELS' },
      letterSpacing: { value: 0, unit: 'PIXELS' }
    };
    if (color) textNode.color = color;
    nodes.push(textNode);
    return nodes;
  }

  const bgColor = parseCssColor(style.backgroundColor);
  const borderColor = parseCssColor(style.borderColor);
  const borderWidth = parseFloat(style.borderWidth) || 0;
  const borderRadius = parseFloat(style.borderRadius) || 0;
  const opacity = parseFloat(style.opacity);

  let nodeType = 'FRAME';
  if (el.tagName === 'IMG' || el.tagName === 'SVG') nodeType = 'RECTANGLE';
  else if (el.children.length === 0 && bgColor) nodeType = 'RECTANGLE';

  const node = {
    type: nodeType,
    name: el.tagName.toLowerCase() + (el.id ? '-' + el.id : el.className ? '-' + el.className.split(' ')[0] : ''),
    x: Math.round(x),
    y: Math.round(y),
    width: Math.round(rect.width),
    height: Math.round(rect.height)
  };

  if (bgColor) node.fills = { type: 'solid', color: bgColor };
  if (borderColor && borderWidth > 0) {
    node.strokes = { type: 'solid', color: borderColor };
    node.strokeWeight = borderWidth;
    node.strokeAlign = 'INSIDE';
  }
  if (borderRadius > 0) node.cornerRadius = borderRadius;
  if (!isNaN(opacity) && opacity < 1) node.opacity = opacity;

  const shadows = parseBoxShadow(style.boxShadow);
  if (shadows.length > 0) node.effects = shadows;

  const display = style.display;
  if (display === 'flex') {
    node.layoutMode = style.flexDirection === 'column' ? 'VERTICAL' : 'HORIZONTAL';
    node.itemSpacing = parseFloat(style.gap) || 0;
    const justify = style.justifyContent;
    if (justify === 'center') node.primaryAxisAlignItems = 'CENTER';
    else if (justify === 'space-between') node.primaryAxisAlignItems = 'SPACE_BETWEEN';
    else if (justify === 'flex-end') node.primaryAxisAlignItems = 'MAX';
    else node.primaryAxisAlignItems = 'MIN';

    const align = style.alignItems;
    if (align === 'center') node.counterAxisAlignItems = 'CENTER';
    else if (align === 'flex-end') node.counterAxisAlignItems = 'MAX';
    else node.counterAxisAlignItems = 'MIN';

    node.paddingTop = parseFloat(style.paddingTop) || 0;
    node.paddingRight = parseFloat(style.paddingRight) || 0;
    node.paddingBottom = parseFloat(style.paddingBottom) || 0;
    node.paddingLeft = parseFloat(style.paddingLeft) || 0;
  }

  const childNodes = [];
  for (const child of el.children) {
    childNodes.push(...domToFigmaNodes(child, rect));
  }
  if (childNodes.length > 0) node.children = childNodes;

  nodes.push(node);
  return nodes;
}

function domToFigmaJSON(rootEl) {
  const rootRect = rootEl.getBoundingClientRect();
  const figmaNodes = domToFigmaNodes(rootEl, rootRect);

  // Unwrap body wrapper
  const cleanNodes = figmaNodes.flatMap(n => {
    if (n.type === 'FRAME' && n.name === 'body' && n.children) return n.children;
    return n;
  });

  return { version: '1.0', nodes: cleanNodes };
}

// Export for module or global use
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { domToFigmaJSON, domToFigmaNodes, parseCssColor, parseBoxShadow };
} else {
  window.domToFigmaJSON = domToFigmaJSON;
  window.domToFigmaNodes = domToFigmaNodes;
}
