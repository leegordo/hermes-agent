---
name: doodlehaus-campaigns
description: Operate the DoodleHaus campaign pipeline — run end-to-end campaigns, troubleshoot failures, and migrate the pipeline when upstream frameworks change.
trigger: |
  User mentions DoodleHaus, campaign pipeline, run_pipeline.py, brief JSON, brand KB, 
  or wants to generate a marketing campaign bundle (copy + images + video + publishing checklist).
  Also triggers when fixing broken pipeline scripts or updating model names in doodlehaus/scripts/.
---

# DoodleHaus Campaign Pipeline

## What This Skill Covers

DoodleHaus is an 8-agent campaign execution pipeline. A brief JSON goes in, a complete multi-channel campaign bundle comes out: copy, images, video, and a Publishing Checklist.

The pipeline lives at `~/Projects/doodlehaus/` on the VPS.

## Architecture

```
Brief JSON → Orchestrator → Research → Copy → Creative Direction → Asset Generation → QA → Packaging
```

| Step | Output File | What It Does |
|---|---|---|
| Orchestrator | `campaign-context.md` | Validates brief, creates folder structure, campaign manifest |
| Research | `research.md` | Audience analysis, competitive positioning, messaging framework |
| Copy | `copy-humanized.md` | 3 variants (A/B/C) per channel, format-compliant |
| Creative Direction | `creative-direction.md` | Image prompts + video concept per channel/variant |
| Asset Generation | `assets/manifest.md` | Runs Imagen 4 + Veo, generates images/video |
| QA | `qa-report.md` | Brand voice audit, format compliance, fact check |
| Packaging | `publishing-checklist.md` | Final bundle with per-channel paste instructions |

## Running a Campaign

```bash
cd ~/Projects/doodlehaus

# Set Gemini API key (needed for text generation + image/video gen)
export GEMINI_API_KEY=*** Run full pipeline
python3 scripts/run_pipeline.py briefs/CLIENT-001.json --stack B

# Restart from beginning (ignore prior state)
python3 scripts/run_pipeline.py briefs/CLIENT-001.json --restart
```

Output lands in `campaigns/{campaign_id}/`.

## Brief Format

Briefs are JSON files in `briefs/`:

```json
{
  "campaign_id": "20260609-client-001",
  "client": "clientslug",
  "goal": "string",
  "audience": "string",
  "product_or_service": "string",
  "key_messages": ["msg1", "msg2"],
  "channels": ["twitter", "linkedin_post", "nostr", "reddit", "landing_page"],
  "model_stack": "B",
  "tone_notes": "builder-to-builder, direct",
  "community_context": "optional"
}
```

**Required:** client, goal, audience, product_or_service, key_messages, channels, model_stack.

**Channels:** linkedin_post, linkedin_carousel, twitter, nostr, cold_email, landing_page, google_ads, reddit, instagram_post, meta_carousel.

**Model Stacks:**
- **A (Budget):** gemini-2.5-flash for most steps
- **B (Standard):** gemini-2.5-pro for copy/creative, gemini-2.5-flash for rest
- **C (Premium):** gemini-2.5-pro for everything

## Brand KB

Each client needs a Brand KB at `brand-kb/{client-slug}.md`. Copy `brand-kb/TEMPLATE.md` and fill all 6 sections:

1. Foundation (positioning, mission, voice/tone, personas)
2. Services/Products Catalog
3. Channel-Specific Rules
4. Portfolio / Proof Points
5. Competitor Intel
6. Community Context

## Critical Pitfalls

### 1. Pipeline Uses Direct Gemini API Calls (Not Sub-Agents)

The original `scripts/run_pipeline.py` (v1) spawned sub-agents via an OpenClaw gateway. That gateway no longer exists. The current script (v2) calls the Gemini API directly for each step.

**If the pipeline fails with "OPENCLAW_GATEWAY_TOKEN not set":** The repo still has the old v1 script. The fix is in `references/pipeline-v2-rewrite.md` — replace sub-agent spawning with direct `requests.post()` to `generativelanguage.googleapis.com`.

### 2. Gemini Model Names Change Frequently

Google deprecates model names without warning. The pipeline defaults must be kept current.

| Status | Model Name |
|---|---|
| ✅ Working | `gemini-2.5-flash` |
| ✅ Working | `gemini-2.5-pro` |
| ❌ Deprecated | `gemini-2.0-flash` (returns 404) |
| ❌ Deprecated | `gemini-2.5-pro-preview-06-05` (returns 404) |
| ❌ Deprecated | `gemini-1.5-flash` (returns 404) |
| ❌ Deprecated | `gemini-1.5-pro` (returns 404) |

**Fix:** Update `scripts/run_pipeline.py` — search for all `model="..."` in step functions and replace deprecated names with `gemini-2.5-flash` (fast/cheap steps) or `gemini-2.5-pro` (complex generation steps: copy, creative direction).

### 3. API Key Format Matters

- **Google AI Studio keys** start with `AIzaSy...` — these work for both text generation AND Imagen/Veo.
- **OAuth tokens** (start with `AQ.`, `ya29.`, etc.) are for Google Cloud OAuth flows and will fail with "API key not valid".
- If the user provides an `AQ.` token, it is likely an OAuth access token, not an API key. Ask for the AI Studio key instead, or rewire the pipeline to use the existing Hermes LLM provider for text and only use Imagen/Veo if a valid AI Studio key is available.

### 4. Asset Generation Requires Valid Key + Working Scripts

Images: `scripts/generate_image.py` — uses `google-genai` SDK, needs `GEMINI_API_KEY`.
Video: `scripts/generate_video.py` — same SDK, same key.

If key is invalid, asset generation gracefully skips and writes a manifest noting the failure. The rest of the pipeline (copy, research, QA) still completes.

## Notification Setup

The pipeline sends Signal notifications via `hermes send`. If Signal is not configured, notifications silently fall back to console output.

## References

- `references/pipeline-v2-rewrite.md` — How the v1 → v2 rewrite works (OpenClaw sub-agents → direct API)
- `references/gemini-model-aliases.md` — Current working model names and their deprecated predecessors
