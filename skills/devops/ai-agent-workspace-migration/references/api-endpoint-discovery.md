# API Endpoint Discovery — When Docs Don't Match Reality

When migrating scripts that call third-party APIs, the documented endpoints may be incomplete, deprecated, or outright wrong. This reference documents a reproducible probe pattern using the PayPerQ (PPQ) API as a case study.

## The Problem

PPQ's docs list `https://api.ppq.ai/v1/chat/completions` as the primary endpoint, but provide **no balance or credit-check endpoint**. A legacy script expected to monitor credits by calling a `/credits` or `/billing` endpoint. None exist.

## The Probe Pattern

When you need to discover what endpoints actually work:

```python
import requests, json, os

token = os.getenv('API_KEY')
base = 'https://api.ppq.ai/v1'

# Test common credit/balance endpoint patterns
for path in ['user', 'account', 'billing', 'billing/credits', 'credits', 'balance', 'usage']:
    r = requests.get(f"{base}/{path}", headers={"Authorization": f"Bearer {token}"}, timeout=15)
    print(f"GET /{path}: {r.status_code} - {str(r.json())[:200]}")
```

**Result:** All returned `404` with a generic `"OOPS! - 404 Not Found"` body.

## The Functional Test

When balance endpoints don't exist, the practical test is a **minimal real request**:

```python
r = requests.post(
    f"{base}/chat/completions",
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    json={"model":"openai/gpt-4.1-nano","messages":[{"role":"user","content":"hi"}],"max_tokens":20},
    timeout=15
)
data = r.json()
```

**Key observations from the response:**
- `status_code == 200` → token is valid and account has credits
- `data['usage']` contains `cost`, `cost_details` → billing info is returned per-request, not via a separate endpoint
- `402 Payment Required` → account is out of credits (this is the actual failure mode to monitor)

## General Pattern

| Step | Action | Why |
|------|--------|-----|
| 1 | Read the docs for a "balance" or "status" endpoint | Sets expectations |
| 2 | Probe common path patterns (`/billing`, `/credits`, `/usage`, `/account`) | Finds undocumented endpoints |
| 3 | Make a minimal real request with the cheapest model/params | Verifies auth and detects 402 |
| 4 | Inspect response headers for rate-limit or quota info | Some APIs put balance in headers |
| 5 | If no balance endpoint exists, design monitoring around the **failure mode** (402) rather than the **balance** | More robust — tells you when you're cut off |

## Application to Migration

When a legacy cron job monitored "PPQ credits < $10," the correct rewrite is:
- **Option A:** Remove the cron. The user will discover they're out of credits when their next message to the agent fails with a 402. This is acceptable if the cost of being briefly offline is low.
- **Option B:** Create a cron that makes a 1-token test request and alerts on any non-200 status. This catches 402s without needing a balance number.

**Do not** block migration waiting for a balance endpoint that doesn't exist.
