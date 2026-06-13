---
name: agent-creative-quality
description: "Improve the output quality of creative AI agents (design, writing, visual, UX) by adding a taste/principles layer and hardening the critique loop. Use when subagents produce compliant but generic, template-like, or low-quality creative output."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [agents, subagents, creative, quality, prompt-engineering, design, critique]
    related_skills: [subagent-driven-development, claude-code, portfolio-website-redesign]
---

# Agent Creative Quality

When AI subagents produce output that is technically correct but creatively poor — token-compliant design that looks like a Bootstrap template, copy that reads like AI slop, visuals with no hierarchy or focal point — the problem is rarely missing rules. The problem is missing **taste**.

This skill provides a repeatable pattern for elevating creative agent output from "follows the spec" to "feels intentional and crafted."

## When to use this skill

- Subagent output is technically correct but generic, flat, or template-like
- User complains that agent output "looks like AI slop" or "feels corporate"
- Agents follow all rules but produce no visual tension, no hierarchy, no brand voice
- The critique loop catches token drift but misses composition, rhythm, and taste
- You need to harden a creative agent system (design, writing, visual, UX) for production quality

## The root cause

Creative agents typically have:
- **Rules** (what values are legal, what tokens to use, what components exist)
- **Constraints** (don't invent values, don't hardcode hex, use the DS)
- **Process** (generate three concepts, pick one, iterate)

They typically lack:
- **Taste** (what good looks like for this specific brand/domain)
- **Composition sense** (hierarchy, scan path, whitespace rhythm, focal points)
- **Anti-pattern awareness** (what generic/template output looks like and why to avoid it)
- **Scored critique dimensions** (structured quality scoring beyond token compliance)

## The fix: add a taste layer

The pattern has four parts. Apply all four — partial application produces partial results.

### Part 1: Create a `design-principles` (or `creative-principles`) skill

This is the taste bible. It lives in `skills/` and is loaded by both generator and critic agents before they work.

**What it must contain:**

1. **Philosophy** — 2–3 words that define the brand's creative identity (e.g., "Confident, Playful, Trustworthy") plus what the enemy is (e.g., "generic SaaS template output")
2. **Composition rules** — concrete, actionable rules:
   - Scan patterns (F-pattern, Z-pattern, centered for short statements)
   - Whitespace discipline (section gaps, internal padding, breathing room around CTAs)
   - Grid rules (max-width, column splits, card grid columns)
   - Type hierarchy (staircase rules, max-width for body text, font family discipline)
3. **Color strategy** — what each color means, what it's for, and what it's NOT for. Include anti-patterns (e.g., "never use brand red for backgrounds")
4. **Image/asset treatment** — size, radius, shadow, authenticity rules
5. **Interaction rules** — hover, focus, loading, empty states
6. **Layout patterns** — 2–3 proven patterns for this brand/domain, with section-by-section breakdowns
7. **Anti-patterns** — named, recognizable failure modes that trigger automatic rejection. Give each a memorable name:
   - "The Bootstrap Look" — card grid with identical cards, grey borders, blue links
   - "The Dashboard Default" — dark sidebar, white content, metric cards in 4-up grid
   - "The Startup Template" — giant gradient hero, 3 feature icons, floating device mockup
   - "The Muted Palette" — everything grey, CTA is the only color
   - "The Type Salad" — >4 font sizes, mixed alignment, inconsistent weights
   - "The Button Forest" — multiple primary-colored buttons competing
   - "The Ghost Page" — loads of whitespace with tiny centered text
8. **Self-critique checklist** — 6–10 questions the generator agent must answer in writing before handoff
9. **Critique dimensions** — 4–6 scored dimensions (1–5) for the critic agent:
   - Hierarchy, Rhythm, Tension, Brand voice, Conversion clarity, Token fidelity

**What it must NOT contain:**
- Token values (those belong in the design system / tokens file)
- Component specs (those belong in components.json)
- Technical stack rules (those belong in the frontend-design skill)

The principles skill is about **taste and composition**, not mechanics.

### Part 2: Harden the generator agent

Modify the generator agent (e.g., `mia.md`) to:

1. **Require the principles skill as a read** — add it to the required reads list, before tokens/components
2. **Plan visually before coding** — add a step: "Sketch the composition in words first: focal point, scan path, whitespace rhythm. Write a 3–5 bullet layout plan and include it in the report."
3. **Self-critique before handoff** — add a step: "Run the Self-Critique Checklist from the principles skill. Write answers in the report. If any answer is weak, fix the concept before submitting."
4. **Self-reject anti-patterns** — add a rule: "Reject your own work if it matches any anti-pattern from the principles skill. Iterate until it feels like [Brand], not a template."
5. **Include layout plan and self-critique in reporting format** — add `📐 Layout plan` and `🧪 Self-critique` sections to the agent's output template

### Part 3: Harden the critic agent

Modify the critic agent (e.g., `dieter.md`) to:

1. **Require the principles skill as a read** — add it to required reads
2. **Critique visually first, then mechanically** — add a step: "Before checking token compliance, ask: does this have a clear focal point? Does the scan path work? Does it feel like [Brand] or a template?"
3. **Score on critique dimensions** — require a 1–5 score on each dimension from the principles skill
4. **Automatic rejection thresholds** — add rules:
   - Score ≤2 on any dimension = automatic rejection with specific diagnosis
   - Score ≤3 on Brand voice = automatic rejection (token compliance is table stakes)
   - Any anti-pattern match = automatic rejection, name the anti-pattern
5. **Specific actionable feedback** — add a rule: "'It feels flat' is not feedback. 'The hero has no focal point because the headline and image compete at equal visual weight — either enlarge the headline or give the image a subtle shadow to recede' is feedback."
6. **Include critique scores in reporting format** — add `📊 Critique scores` section

### Part 4: Harden the audit skill

Modify the audit skill (e.g., `audit-design-system.md`) to:

1. **Require the principles skill as a read**
2. **Add visual quality as an audit dimension** — score on the same critique dimensions
3. **Add anti-patterns as an audit dimension** — check against the named anti-patterns
4. **Include visual quality scores in output format** — add a scored table to the audit report

### Part 5: Harden the orchestration commands

Modify the commands that spawn agents (e.g., `design-process.md`, `prototype.md`) to:

1. **Load the principles skill for both generator and critic**
2. **Require visual quality scores in critique output**
3. **Require anti-pattern checks in critique output**
4. **Pass the principles skill path in the agent spawn payload**

## Verification

After applying this pattern, agent output should:
- Include a written layout plan before code
- Include self-critique answers in the report
- Include critique dimension scores (1–5) in review
- Be rejected automatically for anti-pattern matches
- Feel specific to the brand/domain, not generic

## Example: before and after

**Before:**
> Mia generates three concepts. They differ only in border radius and whether the CTA is left or center aligned. Dieter checks token compliance and gives a pass. The output looks like every other Tailwind UI kit.

**After:**
> Mia plans the composition first: "Focal point is the 72px Encode Sans headline. Scan path leads down the left edge to the CTA band. Whitespace: 80px between hero and features." She self-critiques: "Anti-pattern check: this follows Pattern A from principles, not a template." Dieter scores: Hierarchy 4/5, Rhythm 5/5, Tension 3/5, Brand voice 5/5, Conversion clarity 4/5, Token fidelity 5/5. The output feels like StickerGiant.

## Rules

- The principles skill must be about taste and composition, not mechanics (tokens, components, stack)
- Anti-patterns must be named and recognizable — vague descriptions don't trigger self-rejection
- Critique dimensions must include at least one "soft" dimension (Brand voice, Tension) that can't be linted mechanically
- Both generator and critic must load the principles skill — loading it for only one side creates a mismatch
- The orchestration commands must explicitly pass the skill in spawn payloads — don't assume agents will find it
