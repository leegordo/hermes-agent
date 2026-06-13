---
Session: 2026-05-28 (continuation)
Host: Ubuntu 24.04, signal-cli 0.14.4.1, OpenJDK 25
Goal: Complete Signal setup for Hermes gateway after linking +525XXXX3563
---

## Issue: signal-cli daemon conflict with CLI commands

After linking the device, `signal-cli listAccounts` and other CLI commands timed out or returned "Config file is in use by another instance". This occurs when the HTTP daemon (`signal-cli daemon --http ...`) holds the account database lock, preventing concurrent CLI access.

### Resolution

Either:
1. **Use the daemon's HTTP API for everything** (Hermes does this natively), OR
2. **Stop the daemon** before running CLI commands using `pkill -f 'signal-cli daemon'`.

Do NOT try to run `signal-cli send` while the daemon is active on the same account.

## Issue: Java compatibility with signal-cli 0.14.4.1

Same as Session-specific-setup-log.md — Java 25 required.

## Issue: signal-cli outputs link URI to stdout but also stderr noise

The `link` command prints the `sgnl://linkdevice?...` URI to stdout but returns "Link request error: Connection closed!" to stderr when the 2-minute timeout expires. If both streams are captured to the same file (e.g. `> /tmp/file 2>&1`), the file contents become contaminated with error text, breaking URI parsing.

### Resolution

Capture streams separately:
```bash
timeout 120 signal-cli link > /tmp/signal.uri 2>/tmp/signal.err &
# OR
(signal-cli link 2>/dev/null | head -1) > /tmp/signal.uri
```

## Hermes adapter behavior after linking

Hermes gateway reads `SIGNAL_ACCOUNT` from `.env`. The adapter checks `SIGNAL_HTTP_URL` and `SIGNAL_ACCOUNT` at startup. If set correctly, `hermes status --all` shows:

```
Signal        ✓ configured
```

Gateway logs show SSE connection cycling:
```
gateway.platforms.signal: Signal SSE: connected
```

If `SIGNAL_ACCOUNT` mismatches the actual linked number in signal-cli, outbound sends fail silently or with HTTP 500 from the daemon.

## Env configuration (.env)

```bash
SIGNAL_HTTP_URL=http://127.0.0.1:8080
SIGNAL_ACCOUNT=+525****3563
SIGNAL_ALLOWED_USERS=+141****8448
```

`SIGNAL_ALLOWED_USERS` must be set explicitly — do not rely on `*` in production.

## Important: signal-cli linked number vs user texting number

In this session, signal-cli linked to `+525****3563`. The user also has `+141****8448` but that is NOT linked to signal-cli — it is the number the user texts FROM. Hermes receives messages at +525XXXX3563 and must be configured with that number as `SIGNAL_ACCOUNT`.

Always verify the linked number from `accounts.json` or `listAccounts` before writing `.env`.

## Daemon startup

```bash
background process:
  signal-cli daemon --http 127.0.0.1:8080

then verify:
  curl -s http://127.0.0.1:8080/api/v1/check
```
