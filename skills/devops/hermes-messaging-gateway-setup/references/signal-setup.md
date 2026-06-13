# Signal — Hermes Gateway Setup Reference

Connect Signal to Hermes via signal-cli's HTTP daemon mode.

## Architecture

```
Signal app (phone, primary device)
     ↕ device link (sync)
signal-cli daemon --http 127.0.0.1:8080  (secondary device)
     ↕ SSE inbound + JSON-RPC outbound
Hermes SignalAdapter (gateway/platforms/signal.py)
```

## Prerequisites

- Hermes Agent installed, gateway service running
- OpenJDK 25+ (signal-cli v0.14.4.1+ requires class-file version 69)
- Phone with Signal app installed

## 1. Install Java 25

```bash
java -version 2>&1
# If version < 25:
apt-get update && apt-get install -y openjdk-25-jre-headless
```

> **Pitfall:** signal-cli 0.14.4.1 fails on Java 21 with `UnsupportedClassVersionError`.

## 2. Install signal-cli

```bash
mkdir -p /opt/signal-cli && cd /opt/signal-cli
VERSION="0.14.4.1"
curl -fsSL -o signal-cli.tar.gz \
  "https://github.com/AsamK/signal-cli/releases/download/v${VERSION}/signal-cli-${VERSION}.tar.gz"
tar xzf signal-cli.tar.gz
ln -sf /opt/signal-cli/signal-cli-${VERSION}/bin/signal-cli /usr/local/bin/signal-cli
signal-cli --version
```

## 3. Link Device (Recommended over Register)

Registering makes signal-cli the primary device and de-registers your phone. Linking keeps your phone as primary.

```bash
# Start link process (times out after ~2 min)
timeout 120 signal-cli link > /tmp/signal-link.uri 2>&1 &
sleep 3
URI=$(cat /tmp/signal-link.uri | tr -d '\n')

# Display QR code for scanning
apt-get install -y qrencode
qrencode -t ansiutf8 "$URI"
```

**User:** Signal app → Settings → Linked Devices → Link New Device → scan QR.

**Verify:**
```bash
signal-cli listAccounts
# → shows your linked phone number E.164 format (+1...)
```

> **Pitfall:** The QR URI expires in ~2 minutes. For async/remote sessions where the user is not immediately ready, use the `sgnl://` URI directly in a standalone QR generator instead of relying on terminal rendering. ASCII block-art QR (`qrencode -t ansiutf8`) is unreliable across terminal fonts and scrollback; prefer image-based or hosted QR. If the URI is malformed by stderr noise in the capture file, extract only the first line (`head -1`) before rendering.

> **Pitfall:** signal-cli stores account data in `~/.local/share/signal-cli/`. Do NOT mix up account numbers when configuring `SIGNAL_ACCOUNT` in Hermes `.env` — use the number shown in `signal-cli listAccounts` (or `accounts.json`), not the user's personal texting number. Capturing the correct linked account number early prevents auth failures and HTTP 404 errors from the Hermes adapter.

## 4. Start Daemon

```bash
signal-cli daemon --http 127.0.0.1:8080
```

Verify reachable:
```bash
curl -s http://127.0.0.1:8080/api/v1/check
```

## 5. Configure Hermes

Edit `~/.hermes/.env`:

```bash
SIGNAL_HTTP_URL=http://127.0.0.1:8080
SIGNAL_ACCOUNT=+123****5678          # your E.164 phone number
SIGNAL_ALLOWED_USERS=*               # or comma-separated numbers
# SIGNAL_GROUP_ALLOWED_USERS=+12...  # empty = groups disabled
# SIGNAL_REQUIRE_MENTION=true        # only reply in groups when @mentioned
# SIGNAL_HOME_CHANNEL=+123****5678
# SIGNAL_HOME_CHANNEL_NAME=Home
```

Restart gateway:
```bash
hermes gateway restart
```

## 6. Verify

```bash
hermes status --all | grep -A5 Signal
```

Should show `Signal: configured`.

## Authorization

| Setting | Env var | Behavior |
|---------|---------|----------|
| DM allowlist | `SIGNAL_ALLOWED_USERS` | `*` = open; otherwise comma-separated E.164 numbers |
| Group allowlist | `SIGNAL_GROUP_ALLOWED_USERS` | Empty = ignore all group messages |
| Mention filter | `SIGNAL_REQUIRE_MENTION` | `true` = only reply in groups when @mentioned |

## Daemon Auto-Start (systemd user service)

```ini
# ~/.config/systemd/user/signal-cli-daemon.service
[Unit]
Description=signal-cli HTTP daemon
After=network.target

[Service]
ExecStart=/usr/local/bin/signal-cli daemon --http 127.0.0.1:8080
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
```

```bash
systemctl --user daemon-reload
systemctl --user enable --now signal-cli-daemon
```

## Hermes Signal Adapter Internals

File: `/usr/local/lib/hermes-agent/gateway/platforms/signal.py`

- Inbound: SSE (`/api/v1/events`) streaming from signal-cli
- Outbound: JSON-RPC over HTTP (`send`, `sendReaction`, `sendTyping`)
- Supports: text, images, audio, video, documents, reactions, typing indicators
- Rate limiting: built-in scheduler for attachment batching
- Group mention filter: `SIGNAL_REQUIRE_MENTION`
- Self-message filter: prevents echo loops
- Note to Self: supported (syncMessage → dataMessage promotion)

## TLS Certificate Fix

If `signal-cli link` outputs a URI then immediately fails with "Connection closed!", Signal's self-signed certificate may not be in Java's trust store:

```bash
openssl s_client -connect chat.signal.org:443 -servername chat.signal.org \
  </dev/null 2>/dev/null | openssl x509 -outform PEM > /tmp/signal-cert.pem

JAVA_CACERTS=$(find /usr -name "cacerts" | head -1)
keytool -import -trustcacerts -alias signal-messenger \
  -file /tmp/signal-cert.pem -keystore "$JAVA_CACERTS" \
  -storepass changeit -noprompt
```

## SMS Registration (Fallback)

If device linking fails, register signal-cli as a standalone primary device:

1. Get CAPTCHA token: visit `https://signalcaptchas.org/registration/generate.html`
2. Right-click "Open Signal" → copy link address
3. Extract the token from the `signalcaptcha://...` URI
4. Register:
   ```bash
   signal-cli -a +PHONE_NUMBER register --captcha TOKEN
   signal-cli -a +PHONE_NUMBER verify SMS_CODE
   ```

> **Warning:** Registering makes signal-cli the primary device and de-registers your phone. Linking (above) is strongly preferred.

## Workflow Preference

When a presentation approach (QR codes, web servers, image hosting) encounters repeated friction, **pivot early to simpler alternatives** rather than iterating on rendering workarounds. Users prefer a working text-based fallback (the raw `sgnl://` URI) over a theoretically elegant but practically broken visual solution.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `UnsupportedClassVersionError` | Java < 25 | Install `openjdk-25-jre-headless` |
| "Connection closed!" after URI | TLS cert rejected or link timed out | Import Signal CA cert; generate fresh link quickly |
| "Config file is in use" | Daemon running | Use HTTP API instead of CLI, or stop daemon first |
| "Invalid account" | Wrong `-a` format | Use full E.164: `+countrycode...` |
| "UNREGISTERED_FAILURE" | Recipient not on Signal | Verify recipient has active Signal account |
| `404 Not Found` on HTTP API | Wrong endpoint | Use `/api/v1/rpc` for JSON-RPC, not `/api/v1/messages` |
| "Specified account does not exist" | Multi-account mode mismatch | Omit `account` param if only one account linked |
