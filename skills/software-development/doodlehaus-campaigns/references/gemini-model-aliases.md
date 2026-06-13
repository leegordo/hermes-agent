# Gemini Model Name Quick Reference

Last verified: 2026-06-09

## Currently Working

| Model | Best For | Notes |
|---|---|---|
| `gemini-2.5-flash` | Fast/cheap steps: orchestrator, research, QA, packaging | Replaces deprecated `gemini-2.0-flash` and `gemini-1.5-flash` |
| `gemini-2.5-pro` | Complex generation: copy, creative direction | Replaces deprecated `gemini-2.5-pro-preview-06-05` and `gemini-1.5-pro` |

## Deprecated (Return 404)

| Model | Replacement |
|---|---|
| `gemini-2.0-flash` | `gemini-2.5-flash` |
| `gemini-2.5-pro-preview-06-05` | `gemini-2.5-pro` |
| `gemini-1.5-flash` | `gemini-2.5-flash` |
| `gemini-1.5-pro` | `gemini-2.5-pro` |

## How to Update the Pipeline

```bash
cd ~/Projects/doodlehaus
# Update all model names in run_pipeline.py
sed -i 's/gemini-2\.0-flash/gemini-2.5-flash/g' scripts/run_pipeline.py
sed -i 's/gemini-2\.5-pro-preview-06-05/gemini-2.5-pro/g' scripts/run_pipeline.py
sed -i 's/gemini-1\.5-flash/gemini-2.5-flash/g' scripts/run_pipeline.py
sed -i 's/gemini-1\.5-pro/gemini-2.5-pro/g' scripts/run_pipeline.py
```

## Verification

```python
import requests, os
key = os.environ.get("GEMINI_API_KEY")
for model in ["gemini-2.5-flash", "gemini-2.5-pro"]:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key=***    r = requests.post(url, json={"contents":[{"role":"user","parts":[{"text":"Hi"}]}]}, timeout=10)
    print(f"{model}: {r.status_code}")  # Should be 200
```

## API Key Format

- **Valid:** `AIzaSy...` (Google AI Studio API key)
- **Invalid for Gemini API:** `AQ...` (OAuth access token), `ya29...` (OAuth bearer token)
- If user provides an `AQ.` token, it is an OAuth token. Ask for the AI Studio key from https://aistudio.google.com/app/apikey, or rewire text generation to use the Hermes LLM provider instead.
