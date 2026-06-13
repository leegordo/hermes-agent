# OpenClaw / Lobo Migration Context

Session: 2026-05-28
Server: srv1354161

## Background
User (leegordo) had an OpenClaw deployment previously running in Docker at `/docker/openclaw-mejc/`. The deployment is now missing but backup automation scripts remain in `/root/`.

## What Was Found on Server
- `/docker/` — empty directory
- Docker daemon running but zero images/containers
- Backup scripts exist:
  - `/root/setup_backup_automation.sh` — encrypted daily backups to `/root/openclaw-backups/`
  - `/root/setup_runbook_and_health.sh` — restore runbook + health checks
  - `/root/setup_git_sync_automation.sh` — nightly git sync of config
  - `/root/bootstrap_config_repo.sh` — config backup from live deployment
- No actual backup files at `/root/openclaw-backups/`

## GitHub Repo
- URL: https://github.com/leegordo/Lobo
- Private repo (requires auth)
- User's GitHub username: leegordo

## Auth Method Used
**Stale token + failed device flow → SSH keys as reliable path.**

1. Initial state: `gh auth status` showed prior account `leegordo` with invalid token
2. Tried `gh auth login` device flow **3 times** — user authorized each time, token never persisted
3. Final successful path: SSH key auth
   - `ssh-keygen -t ed25519 -C "hermes@srv1354161" -f /root/.ssh/id_ed25519 -N ""`
   - User added public key to GitHub at https://github.com/settings/keys
   - `git clone git@github.com:leegordo/Lobo.git`

**Lesson:** When `gh auth status` already shows a stale/invalid token for the target account, `gh auth login` device flow is unreliable — the stale state interferes. Logout first (`gh auth logout -h github.com -u <username>`), or better: bypass `gh` entirely and use SSH keys.

## Migration Steps Taken
1. Cloned repo to `/docker/lobo/`
2. Copied workspace contents to `/data/.openclaw/workspace/` with symlink `/data/lobo`
3. Installed missing Python deps: `google-genai`, `google-generativeai`
4. Adopted user profile into Hermes persistent memory
5. Found scripts with hardcoded `/data/.openclaw/` paths and missing `.env`/API keys
6. Pending: fix paths, wire up API keys, set up cron jobs

## Key Files from Lobo Repo
- `SOUL.md` — agent persona (professional with humor, modeled after comic character Lobo)
- `USER.md` — user profile (Lee Gordon, Mexico City, StickerGiant client)
- `IDENTITY.md` — agent identity (Lobo, wolf emoji)
- `TOOLS.md` — local tool notes (Figma API, Cursor Agent, billing tool, Pencil MCP bridge)
- `MEMORY.md` — long-term memory (active tasks, DoodleHaus project, cron jobs list)
- `scripts/` — Python automations (Gmail, health check, security review, image/video gen, TTS)
- `projects/` — DoodleHaus, leegordondesign, stickergiant
- `skills/` — claude-cowork, figma-push-SKILL.md, humanizer

## Next Steps (Pending)
- Fix script paths to point to new workspace location
- Set up `.env` with Gemini API key, Notion token, etc.
- Recreate OpenClaw cron jobs as Hermes cron jobs
- Test key scripts (health check, security review)
