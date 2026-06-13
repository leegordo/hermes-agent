# DESIGN.md Lint Findings & False Positives

Session-accreted knowledge from runs of `@google/design.md lint`.

## 1. Missing `primary` color

The linter warns when no `primary` key exists in `colors:`:

> No 'primary' color defined. The agent will auto-generate key colors, reducing your control over the palette.

**Fix:** Add a `primary:` token mapping to your dominant text/fill color (usually the darkest color on light themes, or lightest on dark themes). This prevents downstream tools from guessing.

## 2. Unreferenced color warnings

Every color token not referenced by a component variant produces a warning:

> 'amber' is defined but never referenced by any component.

These are **not errors** and do not block the build. They indicate the palette is comprehensive but the components section is incomplete. For a fully-specified system this is expected; for a minimal system it suggests cleanup.

## 3. Ghost / transparent button false-positive

A `button-secondary` with `backgroundColor: "transparent"` produces:

> textColor (#1c1510) on backgroundColor (#00000000) has contrast ratio 1.16:1, below WCAG AA

**This is a false positive.** The component is border-dependent; contrast is evaluated against the page, not the transparent fill. No fix needed in the spec.

## 4. Warm-accent WCAG AA recipe

Warm terracotta tones on warm off-white backgrounds often land just below AA (~4.3:1). Rather than lightening the background (which destroys the paper metaphor), **darken the accent**:

```
#B8501A → #A8461A  (drops ~0.5 in lightness, passes AA at 4.5:1+)
```

Keep the hue angle identical; adjust only the lightness channel slightly.

## 5. Bright accent colors on warm paper backgrounds (magenta, cyan, etc.)

Vivid saturated accents — especially fluorescent magenta, cyan, green — often fail WCAG AA on warm cream/paper stock despite being high-chroma. The issue is lightness, not hue.

**Recipe:** Darken until the computed contrast ratio crosses ≥ 4.5:1.

Session example (risograph magenta on paper #F7F2E8):
```
#E8275A → #C91A48  (ratio rises from 3.87:1 to 5.05:1, AA ✓)
```

**Quick Python probe** (open a Python REPL or use `execute_code`):
```python
from hermes_tools import terminal
# Relative luminance formula truncated for brevity —
# use a WCAG calculator or write a 5-line probe
# to binary-search the darkest pass-level hex.
```

The principle: **preserve hue, drop lightness** until AA is met. Document the adjusted hex in the Colors section prose and explain why it's darker than the idealized pigment — accessibility is the justification.

See `references/wcag-probe.py` for a ready-to-run script.

## 5. Extracting only errors from noisy lint JSON

The CLI prints npm engine warnings and deprecation notices to stderr. To get a clean view of structural/validation errors:

```bash
npx -y @google/design.md lint DESIGN.md 2>/dev/null | grep -E '"errors"|"warnings"|"infos"'
```

Or for structured ingestion, redirect stderr to /dev/null before piping to a parser.

## 6. Component variants are flat siblings

Not a lint finding, but a lint enforcer: `button-primary-hover` must be a **sibling** of `button-primary`, not nested under it. Nesting causes parse warnings.
