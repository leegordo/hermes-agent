# DoodleHaus Pipeline v1 → v2 Rewrite

## What Changed

The original `scripts/run_pipeline.py` (v1) relied on **OpenClaw gateway** for sub-agent spawning. Each pipeline step would:

1. Build a massive prompt string
2. Call `_spawn_via_api()` which hit `http://127.0.0.1:{PORT}/tools/invoke` with `sessions_spawn`
3. Poll the child session until it completed
4. Check if the output file was written

This broke when the OpenClaw gateway was removed from the environment.

## v2 Architecture

Each pipeline step now calls the **Gemini API directly** via `requests.post()`:

```python
import requests

url = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    + model
    + ":generateContent?key=***payload = {
    "contents": [{"role": "user", "parts": [{"text": prompt}]}],
    "generationConfig": {
        "temperature": 0.7,
        "maxOutputTokens": 32768,
    },
}

resp = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=120)
text = "".join(p.get("text", "") for p in resp.json()["candidates"][0]["content"]["parts"])
```

The generated text is written directly to the campaign output file. No sub-agents, no gateway, no polling.

## Key Code Changes

### Removed from v1
- `_spawn_via_api()` — sub-agent spawning via OpenClaw gateway
- `_poll_session()` — session polling loop
- `_invoke_tool()` — gateway HTTP client
- `notify_whatsapp()` — replaced with `notify()` via `hermes send`
- `OPENCLAW_GATEWAY_TOKEN`, `OPENCLAW_GATEWAY_PORT` env vars
- `requests` import for gateway calls (kept for Gemini API)

### Added in v2
- `generate_text()` — direct Gemini API caller
- `run_orchestrator()` — previously implicit, now explicit step
- `run_packaging()` — previously implicit, now explicit step
- `slugify()` helper for campaign ID generation
- Fallback key loader: reads `/tmp/gemini_key.txt` if env var is empty

### Modified Steps
All step functions (`run_research`, `run_copy`, `run_creative_direction`, `run_qa`) now:
1. Read input files from disk
2. Build prompt with embedded context
3. Call `generate_text()`
4. Write output to disk
5. Return `True`/`False`

### Asset Generation
`run_asset_generation()` kept the same subprocess calls to `scripts/generate_image.py` and `scripts/generate_video.py`, but simplified prompt extraction from `creative-direction.md` using regex heuristics instead of asking a sub-agent to parse it.

## If You Need to Re-Apply This Pattern

When migrating any pipeline from sub-agent framework to direct API:

1. **Identify the contract:** What does each step receive as input and what does it produce?
2. **Replace spawn logic:** Instead of `spawn_subagent(prompt)`, call the LLM API directly with the same prompt.
3. **File I/O stays the same:** Read previous step's output, write current step's output.
4. **Error handling:** Wrap API calls in try/except, return bool success/failure so the runner can retry or abort.
5. **State/resume:** Keep the JSON state file — it works the same way in v2.
