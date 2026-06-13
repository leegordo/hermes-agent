# Subprocess Environment Isolation in DoodleHaus

## The Problem

`scripts/run_pipeline.py` calls `scripts/generate_image.py` and `scripts/generate_video.py` via `subprocess.run()`. The parent's `GEMINI_API_KEY` module variable does NOT propagate to child processes by default. Child processes only see `os.environ`, not parent-local Python variables.

## The Error

Every image/video generation fails with:
```
Error: GEMINI_API_KEY not set
```

Even though the parent script loaded the key from file.

## The Fix

Pass `env=` explicitly to `subprocess.run()`:

```python
env = os.environ.copy()
if GEMINI_API_KEY:
    env["GEMINI_API_KEY"] = GEMINI_API_KEY
result = subprocess.run(cmd, capture_output=True, text=True, timeout=180,
                        cwd=CAMPAIGN_FACTORY_ROOT, env=env)
```

This must be done for BOTH image and video subprocess calls in `run_pipeline.py`.

## Why This Happens

- `subprocess.run()` without `env=` inherits `os.environ`
- The script's `GEMINI_API_KEY` is a module-level variable, NOT an env var
- Even if `os.environ["GEMINI_API_KEY"]` was set, `subprocess.run()` without `env=` would inherit it — but in this case the env var was a placeholder (`***`), so the fallback-to-file logic in the parent never updated `os.environ`

## Prevention

When a script reads credentials from a fallback file, always:
1. Set `os.environ["KEY"] = value` after reading, OR
2. Pass the key explicitly via `env=` in every subprocess call

Option 2 is safer — it doesn't pollute the global environment.
