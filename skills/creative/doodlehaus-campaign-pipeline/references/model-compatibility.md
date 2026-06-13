# Google Model Compatibility — DoodleHaus

Last tested: 2026-06-10

## Working Models (return 200)

| Model | Use in Pipeline | Notes |
|---|---|---|
| `gemini-2.5-flash` | Orchestrator, Research, QA, Packaging | Fast, sufficient for structured output |
| `gemini-2.5-pro` | Copy, Creative Direction | Heavy output (10k+ chars), needs capacity |

## Deprecated / Broken Models

| Model | Error | When to use |
|---|---|---|
| `gemini-2.0-flash` | 404 "no longer available" | DO NOT USE — replace with 2.5-flash |
| `gemini-1.5-flash` | 404 | DO NOT USE |
| `gemini-1.5-pro` | 404 | DO NOT USE |
| `gemini-2.5-pro-preview-06-05` | unknown | Use stable `gemini-2.5-pro` instead |

## Validation Command

Quick test any model:
```python
import requests
key = "YOUR_KEY"
url = "https://generativelanguage.googleapis.com/v1beta/models/" + model + ":generateContent?key=" + key
r = requests.post(url, json={"contents": [{"role":"user","parts":[{"text":"Hi"}]}]}, timeout=10)
print(r.status_code)
```

## Key Rules
- Keys prefixed with `AQ.` ARE VALID for the API (they are AI Studio keys in a newer format)
- Keys prefixed with `AIzaSy` are classic Google AI Studio keys — also valid
- The `***` placeholder in `.env` files will poison the env var — the script falls back to `/tmp/gemini_key.txt` to avoid this
