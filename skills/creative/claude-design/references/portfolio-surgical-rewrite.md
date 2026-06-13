# Portfolio Surgical Rewrite Checklist

When a user wants to fix their portfolio without a full visual redesign — keep the stack, restructure content and hierarchy.

## Pre-Work: Audit Both Surfaces
1. **Live site** — Screenshot, accessibility tree, verify images load, check mobile
2. **Repo** — package.json (stack), page structure, components, content files (MDX/JSON), tailwind config
3. **Content inventory** — What case studies exist? What testimonials exist? What metrics exist?

## The Six Dimensions (score 1–10)
| Dimension | What to check |
|---|---|
| Positioning | Hero answers: what, for whom, why care? Generic title = fail |
| Proof of Value | Metrics, testimonials, client logos, process evidence |
| Visual Distinctiveness | Template check: dark mode + gradient + card grid + Geist + tracking-wide labels |
| Case Study Quality | Problem → role → process → outcome? Or just name/year/role? |
| Hero Effectiveness | Selling transformation vs. stating identity |
| Technical Execution | Broken images, missing OG tags, performance issues |

## Path A Execution Order
1. **Hero** — Rewrite label, name, tagline. Remove broken video backgrounds. Lead with transformation.
2. **Trust Bar** — Add client names/logos above the fold. Immediately establishes credibility.
3. **Services** — 3 specific offerings, each with a non-generic description that names the actual work.
4. **Projects** — Add `summary` (transformation) and `metric` (proof) fields to frontmatter. Rewrite ProjectCard to surface these instead of skill tags.
5. **Testimonials** — Pull quotes from case studies. Pair each with its key metric. Use metric badges (emerald green).
6. **Pricing/Engagement** — If relevant, add clear engagement models. Reduces friction for prospects.
7. **SEO/Meta** — Update title, description, OG tags, Twitter cards to match new positioning.
8. **About** — Refresh bio to reference new focus area. Update location/contacts.

## Key Content Patterns

### Frontmatter additions for case studies
```yaml
summary: "Built a machine-readable brand system where the rules are the product — consumed by humans, AI agents, and automated workflows."
metric: "Brand review now runs automatically on the majority of content"
```

### Metric badge (React/Tailwind)
```tsx
<span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/5 border border-white/10">
  <svg className="w-3.5 h-3.5 text-emerald-400" .../>
  <span className="text-emerald-400 text-xs font-medium">{metric}</span>
</span>
```

### Testimonial card structure
- Quote in `text-white/60`
- Author name (bold)
- Role/company (muted)
- Metric badge above quote (proves the claim)

## Anti-Patterns to Fix
- Skill tags as primary card content → Replace with summary + metric
- "Product Designer" as hero label → Replace with specific niche
- Video backgrounds that break → Replace with static grid/gradient
- Outdated location/email in footer → Audit and update
- Missing OG/twitter cards → Add metadata for social sharing

## Sign-Off Checklist
- [ ] Build passes (`npm run build`)
- [ ] No broken images in output
- [ ] Meta tags reflect new positioning
- [ ] Content copy uses `&apos;` not raw apostrophes (React/ESLint)
- [ ] Commit message describes the repositioning, not just "update"
