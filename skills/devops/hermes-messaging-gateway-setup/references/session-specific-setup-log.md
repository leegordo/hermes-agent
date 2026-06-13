---
Session: 2026-05-28
Host: Ubuntu 24.04, x86_64, kernel 6.8.0-94-generic
Hermes: installed at /usr/local/lib/hermes-agent
---

## Issue: Java version mismatch

signal-cli v0.14.4.1 downloaded from GitHub releases failed to start with OpenJDK 21:

```
java.lang.UnsupportedClassVersionError: org/asamk/signal/Main has been compiled
by a more recent version of the Java Runtime (class file version 69.0),
this version of the Java Runtime only recognizes class file versions up to 65.0
```

### Resolution

Class file version 69 requires Java 25. Fixed by installing `openjdk-25-jre-headless`:

```bash
apt-get install -y openjdk-25-jre-headless
java -version   # openjdk version "25.0.2" 2026-01-20
```

## Commands that worked

```bash
# 1. Install Java 25
apt-get update && apt-get install -y openjdk-25-jre-headless

# 2. Download signal-cli 0.14.4.1
mkdir -p /opt/signal-cli
cd /opt/signal-cli
curl -fsSL -o signal-cli.tar.gz \
  "https://github.com/AsamK/signal-cli/releases/download/v0.14.4.1/signal-cli-0.14.4.1.tar.gz"
tar xzf signal-cli.tar.gz
ln -sf /opt/signal-cli/signal-cli-0.14.4.1/bin/signal-cli /usr/local/bin/signal-cli
signal-cli --version   # signal-cli 0.14.4.1

# 3. Generate QR for device linking
apt-get install -y qrencode
timeout 120 signal-cli link > /tmp/signal-link.uri 2>&1 &
sleep 3
qrencode -t ansiutf8 "$(cat /tmp/signal-link.uri | tr -d '\n')"
# User scans QR in Signal app → Settings → Linked Devices → Link New Device

# 4. Verify
signal-cli listAccounts

# 5. Start daemon
signal-cli daemon --http 127.0.0.1:8080
```

## Hermes config (.env)

```bash
SIGNAL_HTTP_URL=http://127.0.0.1:8080
SIGNAL_ACCOUNT=+1XXXXXXXXXX   # filled in after linking
SIGNAL_ALLOWED_USERS=*
```

## Gateway status at time of session

Gateway service was already running (PID 3456391) but Signal was not configured.
Other platforms: Telegram, Discord, WhatsApp, Slack, Email, SMS, etc. all unconfigured.
