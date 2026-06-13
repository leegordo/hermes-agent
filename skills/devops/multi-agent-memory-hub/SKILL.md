---
name: multi-agent-memory-hub
description: "Set up and operate a MemPalace hub on a VPS as the always-on memory reconciler for multi-agent workflows. Covers installation, seeding, cross-machine sync testing, and troubleshooting."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [mempalace, memory, sync, hub, vps, multi-agent]
    related_skills: [reconcile, hermes-agent, github-auth]
---

# Multi-Agent Memory Hub (MemPalace on VPS)

## Overview

When running multiple AI agents across machines (Macs with Claude Code, VPS with Hermes), they need shared memory. MemPalace provides vector-searchable memory drawers. The VPS acts as the **always-on hub** — it never sleeps, so it continuously ingests writes from all machines.

**Architecture:**
```
Mac A (Claude Code) → git commit → GitHub → VPS hub → mempalace search
Mac B (Claude Code) → git commit → GitHub → VPS hub → mempalace search
VPS (Hermes) ────────→ git pull ───────┘
```

## Prerequisites

- VPS running Hermes Agent (or any Linux with Python 3.11+)
- GitHub repo `multi-agent-memory` (or equivalent) with `memory/drawers/` directory
- `uv` installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

## Phase 1: Install MemPalace on VPS

### Step 1: Clone the Memory Repo

```bash
mkdir -p ~/Projects
git clone https://github.com/<user>/multi-agent-memory.git ~/Projects/multi-agent-memory
```

If the repo is private, use a classic PAT (fine-grained PATs don't work for git operations):
```bash
git clone "https://<CLASSIC_PAT>@github.com/<user>/multi-agent-memory.git" ~/Projects/multi-agent-memory
```

**Pitfall — dead token in remote URL:** If the repo was previously cloned with an embedded PAT that has since expired, all git operations will fail with `could not read Password`. Check with `git remote get-url origin`. If the URL contains `@github.com` with credentials, strip them:
```bash
git remote set-url origin https://github.com/<user>/<repo>.git
```
Then ensure `git config --global credential.helper store` is set and `~/.git-credentials` has a valid token.

### Step 2: Run Preflight

```bash
cd ~/Projects/multi-agent-memory
./scripts/preflight-vps.sh
```

Checks for: python3, git, uv, hermes, repo presence, git fetch access.

### Step 3: Install MemPalace

```bash
./scripts/install-mempalace-vps.sh
```

This:
- Installs `mempalace` and `mempalace-mcp` via uv
- Bootstraps an empty palace at `~/.mempalace/palace`
- Seeds drawers from `memory/drawers/`
- Wires MCP into `~/.hermes/config.yaml`

**Pitfall — kg_add schema mismatch:** If `seed-mempalace.py` reports `kg_add failed: Internal tool error`, the script is likely passing extra keys (`id`, `name`, `type`, `source`) to `mempalace_kg_add`. The tool only accepts `subject`, `predicate`, `object`, `valid_from`, `valid_to`, and source provenance fields. Also, `entities.jsonl` records lack SPO (subject/predicate/object) and cannot be seeded via `kg_add` — only `observations.jsonl` facts can. Patch `seed-mempalace.py` to strip extra keys and skip entity-only records.

### Step 4: Bootstrap Hermes Integration

```bash
./scripts/bootstrap-hermes.sh
```

Links the reconcile skill to `~/.hermes/skills/` and sets up cron fallback.

### Step 5: Smoke Test

```bash
./scripts/smoke-mempalace-mcp.sh
```

Should report: `OK: found '<test-entity>' via mempalace search`

## Phase 2: Verify Cross-Machine Sync

### The Roundtrip Test

**On a Mac (Claude Code):**

1. Create a test drawer:
```bash
mkdir -p ~/Projects/multi-agent-memory/memory/drawers
cat > ~/Projects/multi-agent-memory/memory/drawers/test_vps_roundtrip_$(date +%Y%m%d).md << 'EOF'
# VPS Roundtrip Test

Written from: MacBook
Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)

This is a cross-machine memory test. If this drawer appears in the
MemPalace on the VPS Hermes agent, the git-as-bus sync is working.

Test content: <unique-verification-phrase>
EOF
```

2. Sync it:
```bash
cd ~/Projects/multi-agent-memory && ./scripts/sync.sh
```

**Pitfall — GitHub email privacy (GH007):**
If push fails with `GH007: Your push would publish a private email address`, the commit was made with a private email. Fix:
```bash
git config --global user.email "<username>@users.noreply.github.com"
git commit --amend --reset-author --no-edit
./scripts/sync.sh
```

**On the VPS (Hermes):**

3. Pull and seed:
```bash
cd ~/Projects/multi-agent-memory
git pull origin main
python3 scripts/seed-mempalace.py
```

4. Verify:
```bash
mempalace search "<unique-verification-phrase>"
```

Should find the drawer with the MacBook timestamp.

## Phase 3: Daily Operations

### Search the Palace

```bash
# Search for anything
mempalace search "cross machine sync"

# Get wake-up context (~600-900 tokens)
mempalace wake-up

# Check health
mempalace status
```

### Manual Hub Sync

```bash
cd ~/Projects/multi-agent-memory
./scripts/hub-sync.sh
```

Pulls latest from GitHub, seeds new drawers, resolves conflicts.

### Health Check (Monitoring)

Run this to verify the hub is actively exporting and the repo is clean:

```bash
cd ~/Projects/multi-agent-memory

# 1. Check manifest last_export timestamps (file is at memory/manifest.json, not repo root)
cat memory/manifest.json | python3 -c "import json,sys;m=json.load(sys.stdin);[print(f\"{c['name']}: {c.get('last_export','null')}\") for c in m['consumers']]"

# 2. Check recent commits are hub exports
git log --oneline -5

# 3. Check repo is clean
git status --short

# 4. Check timer status (may be inactive if using cron instead of systemd)
systemctl is-active multi-agent-memory-sync.timer 2>/dev/null || systemctl --user is-active multi-agent-memory-sync.timer 2>/dev/null || echo "timer not active — check crontab or Hermes cron"
```

**Stall thresholds:**
- `last_export` older than 2 hours → stalled
- No `hub: export` commit in last 5 log entries → stalled
- Uncommitted changes in repo → something is stuck

**Report format:**
- Status: `HEALTHY` | `STALLED` | `BROKEN`
- If `HEALTHY`: one-liner with latest commit time
- If `STALLED`: list what's wrong + suggest `git status` / `git add -A` / `git commit` / `git push` cascade

**Pitfall — manifest.json location:** The manifest is at `memory/manifest.json`, not the repo root. If you `cat manifest.json` from the repo root, it won't exist.

### Scheduled Sync (Cron)

If systemd user session is unavailable (common on VPS), use cron:

```bash
# Edit crontab
crontab -e

# Add: sync every 15 minutes
*/15 * * * * cd ~/Projects/multi-agent-memory && ./scripts/hub-sync.sh >> /tmp/hub-sync.log 2>&1
```

**Alternative: Hermes cron** (when systemd is unavailable and you want logs in Hermes)
```
cronjob create --name mempalace-hub-sync --schedule "*/15 * * * *" \
  --workdir /root/Projects/multi-agent-memory \
  --prompt "Run scripts/hub-sync.sh. Report errors."
```

**Pitfall — systemd user timers:** `bootstrap-hermes.sh` tries to install a systemd user timer, but many VPSes lack a dbus user session (`systemctl --user` fails with "No medium found"). Always verify with `systemctl --user list-timers` after bootstrap; if it fails, fall back to cron or Hermes cron.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `mempalace search` returns nothing new | Palace not re-seeded after git pull | Run `python3 scripts/seed-mempalace.py` |
| `git pull` fails with auth | Token in remote URL is invalid or expired | Update token: `git remote set-url origin https://<TOKEN>@github.com/...` |
| `GH007` on push | Git commit uses private email | Amend with noreply email |
| `smoke-mempalace-mcp.sh` fails | MCP not wired in Hermes config | Re-run `./scripts/install-mempalace-vps.sh` |
| `kg_add failed: Internal tool error` | seed-mempalace.py passes extra keys (`id`, `name`, `type`) to `mempalace_kg_add` which only accepts `subject`, `predicate`, `object`, `valid_from`, `valid_to`, and source fields | Patch seed-mempalace.py to strip extra keys before calling kg_add; skip entity-only records (entities.jsonl lacks SPO) |
| `last_export` stays `null` for VPS hub | export.py only updates the `mempalace` consumer, not `mempalace-vps-hub` | Patch export.py `update_manifest()` to prioritize the `mempalace-vps-hub` consumer |
| `systemctl --user` fails with "No medium found" | VPS lacks dbus user session; systemd timers unavailable | Use Hermes cron (`cronjob` tool) or system crontab instead of bootstrap-hermes.sh systemd path |
| Git remote URL has embedded dead token | Old PAT embedded in clone URL expired | `git remote set-url origin https://github.com/<user>/<repo>.git` — let credential helper handle auth |

## Key Principles

1. **VPS is the source of truth** — it never sleeps, always has the latest reconciled memory
2. **Git is the bus** — GitHub is the canonical transport, not a direct VPS-to-Mac connection
3. **Seed after every pull** — `git pull` doesn't auto-update the palace; always re-seed
4. **Classic PAT for git, fine-grained for API** — Fine-grained PATs work for REST API but not `git clone`/`git push`
5. **Test the roundtrip** — Create a drawer on Mac, sync, search on VPS. If it works, the pipeline works

## References

- `references/session-log-vps-hub-setup.md` — Initial setup log (MemPalace v3.3.5, roundtrip test)
- `references/vps-hub-sync-repair-2026-06-04.md` — Repair session: git remote token cleanup, kg_add schema fix, export.py manifest fix, systemd fallback
