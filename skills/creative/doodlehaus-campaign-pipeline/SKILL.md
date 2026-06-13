---
id: doodlehaus-campaign-pipeline
name: doodlehaus-campaign-pipeline
description: Run DoodleHaus campaign pipeline from brief to campaign bundle. Covers pipeline execution, troubleshooting, and operational maintenance.
triggers:
  - "create a campaign"
  - "run doodlehaus"
  - "pipeline"
  - "brief"
  - "doodlehaus"
  - "generate campaign"
category: creative
---

# DoodleHaus Campaign Pipeline Runner

## What This Does

Takes a JSON brief (in `briefs/`) and produces a complete multi-channel campaign bundle in `campaigns/{campaign_id}/`:

- `campaign-context.md` — validated brief + pipeline manifest
- `research.md` — audience analysis, messaging framework, tone recommendations
- `copy-humanized.md` — 3 variants (A/B/C) per channel
- `creative-direction.md` — image prompts + video concept
- `assets/images/` — channel-optimized images via Imagen 4
- `assets/video/` — campaign video via Veo
- `qa-report.md` — brand voice + format compliance audit
- `publishing-checklist.md` — per-channel paste instructions

## Required Setup

1. **Clone the repo**: `git clone https://github.com/leegordo/doodlehaus.git ~/Projects/doodlehaus`
2. **Google API key** for text + image + video:
   - Place key in `/tmp/gemini_key.txt` (plain text, no newline)
   - The script reads this file if `GEMINI_API_KEY` env var is empty or a placeholder (starts with `***`)
3. **Python deps**: `google-genai` (installed in this environment)
4. **Brief JSON + Brand KB** required before running

## Running the Pipeline

```bash
cd ~/Projects/doodlehaus
python3 scripts/run_pipeline.py briefs/0XC-001.json --restart
```

Resume from last step:
```bash
python3 scripts/run_pipeline.py briefs/0XC-001.json --resume
```

## File Structure

```
doodlehaus/
  briefs/               ← JSON briefs (input)
  brand-kb/             ← per-client knowledge bases
    TEMPLATE.md         ← copy to {client}.md for new clients
  campaigns/{id}/       ← output bundles per run
  agents/               ← agent prompt templates
  scripts/
    run_pipeline.py     ← main runner (THIS FILE)
    generate_image.py   ← Imagen 4 CLI
    generate_video.py   ← Veo CLI
```

## Pipeline Steps (in order)

| Step | Output | Notes |
|---|---|---|
| Orchestrator | `campaign-context.md` + `publishing-checklist.md` (placeholder) | Validates brief, creates folder structure |
| Research | `research.md` | Audience, positioning, messaging, tone |
| Copy | `copy-humanized.md` | 3 variants per channel, humanizer built-in |
| Creative Direction | `creative-direction.md` | Image prompts + video concept |
| Asset Generation | `assets/` + `manifest.md` | Imagen 4 images + Veo video |
| QA | `qa-report.md` | Brand voice + format compliance |
| Packaging | `publishing-checklist.md` (final) | Per-channel publish instructions |

## Operational Pitfalls & Fixes

### API Key Loading

The script falls back to `/tmp/gemini_key.txt` when `GEMINI_API_KEY` env var is missing or a placeholder (`***`). This is **necessary** because the env var may contain a redacted/placeholder value from `.env` files.

```python
# In run_pipeline.py
GEMINI_API_KEY=os.env...Y", "")
_key_file = Path("/tmp/gemini_key.txt")
if _key_file.exists():
    _file_key = _key_file.read_text().strip()
    if _file_key and not _file_key.startswith("*") and len(_file_key) > 10:
        GEMINI_API_KEY=_file_...n### Subprocess Env Isolation

`generate_image.py` and `generate_video.py` are called via `subprocess.run()`. The parent script's `GEMINI_API_KEY` variable is **NOT** automatically inherited by children. Must explicitly pass `env=`:

```python
env = os.environ.copy()
if GEMINI_API_KEY:
    env["GEMINI_API_KEY"] = GEMINI_API_KEY
result = subprocess.run(cmd, ... env=env)
```

### Google Model Deprecation

`gemini-2.0-flash` is deprecated and returns 404. Use `gemini-2.5-flash` (fast/everyday) or `gemini-2.5-pro` (heavy copy/creative tasks). Test models before deploying.

| Task | Model |
|---|---|
| Orchestrator, Research, QA, Packaging | `gemini-2.5-flash` |
| Copy (long output) | `gemini-2.5-pro` with `temperature=0.8` |
| Creative Direction | `gemini-2.5-pro` |

### Asset Generation is Non-Fatal

Campaign should complete even if image/video generation fails. The publishing checklist may note missing assets. In `run_pipeline.py`, asset generation failure is logged but the pipeline continues to QA and packaging.

### Veo Video Timeouts

Veo can take 5+ minutes. The script sets `timeout=300` but video generation may still exceed this. If it times out, the manifest will show 0 video assets. Consider running video generation separately or extending timeout.

### Brief Requirements

Required fields: `client`, `goal`, `audience`, `product_or_service`, `key_messages` (array, min 2), `channels` (array, min 1), `model_stack` ("A" | "B" | "C").
Bonus: `campaign_id` (auto-generated if missing), `tone_notes`, `community_context`.

### Brand KB Template

Each client needs a Brand KB at `brand-kb/{client}.md`. Copy from `brand-kb/TEMPLATE.md` and fill all 6 sections:
1. Foundation (positioning, mission, voice/tone, personas)
2. Services/Products Catalog
3. Channel-Specific Rules
4. Portfolio / Proof Points
5. Competitor Intel
6. Community Context

## Channel Format Rules

These are HARD constraints embedded in the Copy Agent prompt:

- **LinkedIn Post**: plain prose, ≤1300 chars, no hashtags, no markdown headers
- **LinkedIn Carousel**: `[Slide N]` headers, 5-8 slides, ~75 words/slide
- **Twitter/X Thread**: one tweet per line, numbered N/n, ≤280 chars each, 7-9 tweets
- **Nostr Post**: PLAIN TEXT ONLY — zero markdown, zero `**`, `##`, or bullets
- **Cold Email**: Subject line first, 150-250 words per touch, 3 touches separated by `---`
- **Landing Page**: `## Hero`, `## Problem`, `## Solution`, `## Features`, `## Social Proof`, `## CTA`
- **Google Ads**: H1/H2/H3 (≤30 chars), D1/D2 (≤90 chars), show char counts
- **Reddit**: community-native, 300-600 words, no hashtags, no brand links in body
- **Instagram Post**: engaging caption, 2-5 hashtags, emojis welcome
- **Meta Carousel**: `[Slide N]` headers, visual-first narrative

## Notifications

The script uses `hermes send` for Signal notifications at step start/completion. Silent if `hermes` CLI not found. The user prefers minimal notification noise — only critical crons surface output regularly.

## References

- `references/pipeline-state-format.md` — JSON schema for resume state
- `references/model-compatibility.md` — tested Google models and their status
- `references/image-aspect-ratios.md` — per-channel aspect ratio mapping
