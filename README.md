# hermes-agent

Lee's Hermes Agent configuration, skills, cron jobs, and customizations.

**Not the upstream source.** This repo backs up the personal `~/.hermes` directory from the VPS. The Hermes Agent source code lives at [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent).

## What's here

| Path | Description |
|------|-------------|
| `config.yaml` | Main Hermes configuration |
| `SOUL.md` | Agent soul / personality definition |
| `skills/` | Custom and installed skills |
| `cron/` | Scheduled job definitions (`jobs.json`) |
| `scripts/` | Cron scripts (health check, security review, auto-update, etc.) |
| `runbooks/` | Operational runbooks |
| `memories/` | Persistent agent memory (cross-session facts) |
| `images/` | Cached/generated images |
| `hooks/` | Custom gateway hooks |

## Excluded (not committed)

Sensitive and runtime files are excluded via `.gitignore`:

- `.env` — API keys and secrets
- `auth.json` — OAuth tokens
- `state.db` — Session database
- `logs/`, `cache/`, `sessions/`, `sandboxes/` — Runtime data
- `bin/`, `lsp/` — Installed binaries and language servers
- `*.lock`, `*.bak.*` — Lock and backup files

## Sync

Pushed manually from the VPS. To pull changes back:

```bash
cd ~/.hermes
git pull origin main
```

## Auto-update

A daily cron job runs `hermes update --yes --no-backup` at 12:00 UTC. See `scripts/auto-update-hermes.sh`.
