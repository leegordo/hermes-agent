---
name: hermes-messaging-gateway-setup
description: "Set up any messaging platform (Signal, Telegram, Discord, WhatsApp, etc.) on the Hermes Agent gateway. Covers installation, auth, daemon lifecycle, env configuration, and verification."
version: 1.0.0
author: Agent
platforms: [linux]
metadata:
  hermes:
    tags: [hermes, gateway, messaging, signal, telegram, discord, whatsapp]
    related_skills: [hermes-agent]
---

# Hermes Messaging Gateway Setup

Connect messaging platforms to the Hermes Agent gateway so Hermes can receive and reply to messages from each platform.

## General Pattern

Every Hermes gateway platform follows the same high-level pattern:

1. **Prerequisites** — verify Hermes gateway is installed and running.
2. **Platform service** — install and start the platform's bridge/daemon (signal-cli, Baileys, Discord bot, etc.).
3. **Auth / registration** — link a device, get a bot token, or scan a QR code.
4. **Hermes env configuration** — set `*URL`, `*ACCOUNT`/`*TOKEN`, and optional allowlists.
5. **Restart gateway** — `hermes gateway restart`.
6. **Verify** — `hermes status --all` or `hermes gateway status`.

## Hermes Gateway Prerequisite Checks

```bash
# Is the gateway installed?
hermes gateway status

# What platforms are currently configured?
hermes status --all

# Interactive setup wizard (lists all platforms)
hermes gateway setup
```

## Platform-Specific Guides

| Platform | Bridge / Daemon | Auth method | Key env vars |
|----------|-----------------|-------------|--------------|
| **Signal** | signal-cli (`--http`) | Device link (QR) | `SIGNAL_HTTP_URL`, `SIGNAL_ACCOUNT` |
| Telegram | Official Bot API | Bot token from @BotFather | `TELEGRAM_BOT_TOKEN` |
| Discord | discord.py gateway | Bot token + privileged intents | `DISCORD_BOT_TOKEN` |
| WhatsApp | Baileys (built-in) | QR pair via `hermes whatsapp` | `WHATSAPP_ENABLED` |
| Slack | Slack Bolt (Socket Mode) | App + Bot tokens | `SLACK_BOT_TOKEN`, `SLACK_APP_TOKEN` |
| Email | IMAP/SMTP | App password | `EMAIL_ADDRESS`, `EMAIL_PASSWORD` |
| Matrix | matrix-nio | Access token | `MATRIX_HOMESERVER`, `MATRIX_ACCESS_TOKEN` |
| Mattermost | mm-go driver | Personal token | `MATTERMOST_URL`, `MATTERMOST_TOKEN` |

Each platform has a dedicated reference file under `references/` with exact commands and known pitfalls.

## Common Env Configuration Pattern

Most platforms read from `~/.hermes/.env`:

```bash
# Required
<PLATFORM>_URL=...
<PLATFORM>_TOKEN=...        # or <PLATFORM>_ACCOUNT / <PLATFORM>_API_KEY

# Optional allowlists
<PLATFORM>_ALLOWED_USERS=+15551234567,+15559876543
<PLATFORM>_ALLOW_ALL_USERS=false

# Optional home channel (for cron deliveries)
<PLATFORM>_HOME_CHANNEL=<chat_id>
<PLATFORM>_HOME_CHANNEL_NAME=Home
```

After editing `.env`, always restart the gateway:

```bash
hermes gateway restart
```

## Authorization Model

Hermes uses a two-tier auth model for every platform:

1. **DM auth** — who can send DMs to the bot (`*_ALLOWED_USERS` or `*_ALLOW_ALL_users`).
2. **Group auth** — who can mention/tag the bot in groups (platform-specific; often handled by the adapter's `require_mention` logic or a group allowlist).

Open mode (`ALLOWED_USERS=*`) is convenient for personal use but risky for public deployments.

## Troubleshooting

### Gateway not connecting a platform

```bash
# Check logs
grep -i "failed to send\|error" ~/.hermes/logs/gateway.log | tail -20

# Check if the platform adapter requirements are met
# (e.g., signal-cli binary present, Java version correct)
```

### Changes to `.env` not taking effect

- Env vars are read at gateway startup. Always `hermes gateway restart`.
- Some adapters cache config — a full `hermes gateway stop && hermes gateway start` may be needed.

### "No live adapter for platform X" from cron

The platform adapter only exists while the gateway is running. Cron jobs that deliver to a platform need the gateway active. For standalone cron delivery, some platforms provide a `standalone_sender_fn` (see plugin docs).

### Signal: message receipts flow but no real inbound messages reach Hermes

Symptom: `signal-cli` shows receipt messages (delivery/read receipts) in its log, but no actual text messages appear in the gateway log.

Likely causes:
1. **signal-cli NPE bug** — Older versions (≤0.14.4.1) throw `NullPointerException: getServerGuid(...) must not be null` on every inbound message when Signal's server format changes. Upgrade to latest release. See `references/signal-npe-serverguid-fix.md`.
2. **Zombie daemon** — An old signal-cli process is running outside systemd, holding the SQLite lock (`Config file is in use by another instance`). The new systemd-started daemon never fully comes up. `kill -9` the stray process, then `systemctl restart signal-cli`.

Commands to diagnose:
```bash
# Check for NPE — look at signal-cli's log output
journalctl -u signal-cli.service -n 20 --no-pager

# Check for stray process (PID without a systemd parent)
pgrep -a signal-cli
systemctl status signal-cli.service

# If PID differs from systemd's Main PID, the old process is a zombie
ss -tlnp | grep 8080     # Should show systemd-owned PID
```

## References

- `references/signal-setup.md` — Full Signal walkthrough: Java 25 requirement, signal-cli install, device linking, QR generation, daemon start.
- `references/session-specific-setup-log.md` — Timestamped log from a real Signal setup session (host: Ubuntu 24.04, signal-cli 0.14.4.1, OpenJDK 25).
