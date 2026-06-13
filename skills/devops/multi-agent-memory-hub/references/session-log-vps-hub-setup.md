# Session Log: MemPalace VPS Hub Setup

## Environment
- VPS: Hostinger, Ubuntu, AMD EPYC 9354P, 7.8GB RAM
- Hermes Agent v0.14.0
- Python 3.11.15
- MemPalace v3.3.5

## Setup Sequence

```bash
cd ~/Projects/multi-agent-memory
./scripts/preflight-vps.sh      # ✅ passed
./scripts/install-mempalace-vps.sh  # ✅ installed + seeded 6 drawers
./scripts/bootstrap-hermes.sh   # ✅ linked reconcile skill
./scripts/smoke-mempalace-mcp.sh    # ✅ found test entity
```

## Cross-Machine Roundtrip Test

**Mac side (user):**
```
Created: memory/drawers/test_vps_roundtrip_20260530.md
Pushed: commit 153671f — "auto: local writes from Mac @ 20260531T022101Z"
```

**VPS side (Hermes):**
```bash
git pull origin main              # fetched the new drawer
python3 scripts/seed-mempalace.py # imported 1 new drawer
mempalace search "zebra-glacier-1492"  # ✅ found it
mempalace status                   # 7 drawers (was 6)
```

**Result:** PASSED. Git-as-bus sync works end-to-end.

## GitHub Auth Issues Encountered

### Issue 1: Fine-grained PAT doesn't work for git operations
- Fine-grained PAT (`github_pat_11...`) works for API calls (`/repos/owner/repo`)
- Fails for `git clone` with: `Password authentication is not supported for GitHub operations`
- Fails for tarball download with: `HTTP 401 Unauthorized`
- **Fix:** Use classic PAT for git operations, or SSH deploy keys

### Issue 2: GH007 — Private email address
- Push failed: `GH007: Your push would publish a private email address`
- **Fix:** `git config --global user.email "username@users.noreply.github.com"`
- Then amend the commit: `git commit --amend --reset-author --no-edit`

### Issue 3: Shell escaping with underscores
- Fine-grained PATs contain underscores (`github_pat_11...`)
- Bash curl commands with unquoted tokens get mangled
- **Fix:** Use Python/urllib for API calls, or quote variables properly

## Token Storage

Saved to `/root/.env`:
```
GITHUB_CLASSIC_TOKEN=ghp_...     # for git operations
GITHUB_FINEGRAINED_TOKEN=...     # for API calls
```

Cron reminder set for June 27th (29 days before expiry) to notify user.

## Palace Contents After Setup

```
WING: imported
  ROOM: legacy                   6 drawers

WING: multi-agent-memory
  ROOM: cross-machine-test       1 drawer
```

Total: 7 drawers
