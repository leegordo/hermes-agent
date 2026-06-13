# static-site-quality-audit — ARCHIVED

**Status:** Absorbed into `static-site-deployment`
**Date:** 2026-06-09

## Consolidation Reason

This skill was a deployment-aftercare counterpart to `static-site-deployment`.
It covered the same domain (static sites) with a subordinate concern (quality
auditing vs. deploying). A maintainer would write these as one skill with
labeled sections.

All content merged into the umbrella:

- Audit when-to-run triggers → added as "When to audit" subsection
- Link integrity / nav consistency / asset depth checks → merged into existing "Pre-Deploy Audit" section, expanded
- Viewport meta tag check → added as standalone subsection
- Mobile responsive checklist + CSS → added as "Mobile responsive pass" subsection
- Content freshness → added as subsection
- Quick verification commands → added
- Pitfalls (sub-pages, @media blocks, viewport, footer) → added as "Common pitfalls" subsection

## Original Purpose
Systematic quality checks for static HTML/CSS sites—link integrity, nav
consistency, responsive design, asset loading, and content freshness across all
pages including subdirectories.

## Where to find the content now
- `static-site-deployment/SKILL.md` — "## Post-Deploy Quality Audit Checklist" section (lines ~390–483)
