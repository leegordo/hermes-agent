#!/usr/bin/env python3
"""
Binary-search a hex color to find the darkest/lightest variant that passes
WCAG AA (4.5:1) or AAA (7:1) against a background color.

Usage: python wcag-probe.py <bg_hex> <start_hex> [--target aa|aaa]

Example:
  python wcag-probe.py #F7F2E8 #E8275A --target aa
  -> suggests #C91A48 (5.05:1, AA ✓)
"""

import argparse, re, sys


def hex_to_rgb(h):
    h = re.sub(r'[^0-9A-Fa-f]', '', h)
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def relative_luminance(rgb):
    def to_linear(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = to_linear(rgb[0]), to_linear(rgb[1]), to_linear(rgb[2])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(a, b):
    l1, l2 = relative_luminance(a), relative_luminance(b)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def hsl_to_hex(h, s, l):
    def hue_to_rgb(p, q, t):
        t += 1 if t < 0 else 0
        t -= 1 if t > 1 else 0
        if t < 1 / 6:
            return p + (q - p) * 6 * t
        if t < 1 / 2:
            return q
        if t < 2 / 3:
            return p + (q - p) * (2 / 3 - t) * 6
        return p

    if s == 0:
        r = g = b = l
    else:
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue_to_rgb(p, q, h + 1 / 3)
        g = hue_to_rgb(p, q, h)
        b = hue_to_rgb(p, q, h - 1 / 3)
    return '#{:02x}{:02x}{:02x}'.format(int(r * 255), int(g * 255), int(b * 255))


def rgb_to_hsl(rgb):
    r, g, b = rgb[0] / 255, rgb[1] / 255, rgb[2] / 255
    mx = max(r, g, b)
    mn = min(r, g, b)
    l = (mx + mn) / 2
    if mx == mn:
        h = s = 0
    else:
        d = mx - mn
        s = d / (2 - mx - mn) if l > 0.5 else d / (mx + mn)
        if mx == r:
            h = (g - b) / d + (6 if g < b else 0)
        elif mx == g:
            h = (b - r) / d + 2
        else:
            h = (r - g) / d + 4
        h /= 6
    return h, s, l


def darken_until(bg_hex, start_hex, target=4.5, steps=200):
    bg = hex_to_rgb(bg_hex)
    rgb = hex_to_rgb(start_hex)
    h, s, l = rgb_to_hsl(rgb)
    for i in range(steps + 1):
        new_l = max(0, l - (i / steps) * l)  # go to pure black
        cand = hsl_to_hex(h, s, new_l)
        cr = contrast_ratio(hex_to_rgb(cand), bg)
        if cr >= target:
            return cand, cr
    return '#000000', contrast_ratio((0, 0, 0), bg)


def lighten_until(bg_hex, start_hex, target=4.5, steps=200):
    bg = hex_to_rgb(bg_hex)
    rgb = hex_to_rgb(start_hex)
    h, s, l = rgb_to_hsl(rgb)
    for i in range(steps + 1):
        new_l = min(1, l + (i / steps) * (1 - l))
        cand = hsl_to_hex(h, s, new_l)
        cr = contrast_ratio(hex_to_rgb(cand), bg)
        if cr >= target:
            return cand, cr
    return '#FFFFFF', contrast_ratio((255, 255, 255), bg)


def main():
    parser = argparse.ArgumentParser(description='WCAG hex probe')
    parser.add_argument('bg', help='background hex')
    parser.add_argument('start', help='starting accent hex')
    parser.add_argument('--target', choices=['aa', 'aaa'], default='aa')
    args = parser.parse_args()

    target_ratios = {'aa': 4.5, 'aaa': 7.0}
    target = target_ratios[args.target]

    start_c = contrast_ratio(hex_to_rgb(args.start), hex_to_rgb(args.bg))
    if start_c >= target:
        print(f"{args.start}: {start_c:.2f}:1 ✓ (already passes {args.target.upper()})")
        return 0

    # Determine direction: need darker or lighter?
    dark, dark_c = darken_until(args.bg, args.start, target)
    light, light_c = lighten_until(args.bg, args.start, target)

    print(f"_START_ {args.start}: {start_c:.2f}:1 ✗")
    print(f"DARKEN  {dark}: {dark_c:.2f}:1 ✓")
    print(f"LIGHTEN {light}: {light_c:.2f}:1 ✓")

    # Prefer whichever is closest in lightness delta
    hsl_start = rgb_to_hsl(hex_to_rgb(args.start))
    hsl_dark = rgb_to_hsl(hex_to_rgb(dark))
    hsl_light = rgb_to_hsl(hex_to_rgb(light))
    delta_dark = abs(hsl_start[2] - hsl_dark[2])
    delta_light = abs(hsl_start[2] - hsl_light[2])
    if delta_dark <= delta_light:
        print(f"\nRECOMMEND: {dark} (darken by {(delta_dark*100):.1f}% L)")
    else:
        print(f"\nRECOMMEND: {light} (lighten by {(delta_light*100):.1f}% L)")
    return 0


if __name__ == '__main__':
    sys.exit(main())
