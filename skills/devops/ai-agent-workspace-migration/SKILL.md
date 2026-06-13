---
name: ai-agent-workspace-migration
description: "Migrate or restore an AI agent workspace from a legacy deployment, backup repo, or orphaned configuration. Covers discovery, auth, dependency assessment, path rewiring, and automation re-establishment."
version: 1.0.0
author: Hermes Agent
platforms: [linux]
metadata:
  hermes:
    tags: [migration, workspace, ai-agent, restoration, deployment, devops]
    related_skills: [github-auth, hermes-messaging-gateway-setup]
---

# AI Agent Workspace Migration

Migrate or restore an AI agent workspace when the live deployment is missing, the container is gone, or the original platform is deprecated. The goal is to get the agent's memory, scripts, and automations running again on the current infrastructure.

## Trigger Conditions

Load this skill when:
- User says "migrate my X setup" and X is an AI agent workspace (OpenClaw, Lobo, etc.)
- The original deployment directory exists but is empty or stale
- Docker has no containers/images but backup scripts remain
- The user points at a GitHub repo containing an agent workspace (SOUL.md, AGENTS.md, scripts/, memory/)

## Phase 1: Discovery — What Exists?

Before assuming anything, inventory the server:

```bash
# Check for existing deployment directories
find / -maxdepth 3 -type d \( -name "*openclaw*" -o -name "*claw*" -o -name "*lobo*" \) 2>/dev/null

# Check Docker state
docker ps -a --format "table {{.Names}}\t{{.Status}}"
docker images --format "table {{.Repository}}\t{{.Tag}}"

# Check for backup scripts/data
ls -la /root/*backup* /root/*sync* /root/*runbook* 2>/dev/null
find /root -maxdepth 2 -name "*.enc" -o -name "*.tar.gz" 2>/dev/null

# Check for stale auth state
gh auth status 2>/dev/null || echo "gh not configured"
ls -la ~/.ssh/id_* 2>/dev/null || echo "no SSH keys"
```

**Decision:** Is the deployment actually present, or are we working from a backup/repo?

| Scenario | Path |
|----------|------|
| Deployment present, running | Assess health, update config |
| Deployment present, stopped | Start container, verify |
| Deployment missing, backups exist | Restore from backup first |
| Deployment missing, no backups | Clone from GitHub, reconstruct |
| Deployment missing, repo on GitHub | Clone repo, inspect structure |

## Phase 2: Authentication — Get the Code

The workspace likely lives in a private GitHub repo. See `github-auth` skill for full auth setup. Key patterns for this scenario:

### When `gh` Has a Stale Token

```bash
gh auth status
# Shows: "The token in hosts.yml is invalid"
```

**Do not retry device flow.** It will fail to persist. Instead:

```bash
gh auth logout -h github.com -u <username>
# Then either regenerate fresh token, or switch to SSH keys
```

**Preferred path for server migrations:** SSH key auth. Generate a key, have the user add it to GitHub, clone via SSH. No token expiry, no browser dance.

```bash
ssh-keygen -t ed25519 -C "hermes@<hostname>" -f /root/.ssh/id_ed25519 -N ""
cat /root/.ssh/id_ed25519.pub
# User adds to https://github.com/settings/keys
git clone git@github.com:<user>/<repo>.git
```

**Fallback: Token-in-URL clone.** If the user provides a PAT but gh CLI rejects it (missing `read:org` scope, etc.), clone directly:

```bash
git clone https://<token>@github.com/<user>/<repo>.git <dest>
```

This bypasses gh CLI entirely and works with any token that has `repo` read access.

## Phase 3: Structure Inspection — What Are We Migrating?

Clone the repo and identify the workspace type:

```bash
ls -la <repo>/
# OpenClaw/Lobo pattern: SOUL.md, AGENTS.md, MEMORY.md, scripts/, projects/, memory/
# Generic agent pattern: system prompts, tool configs, session data
```

**Reference:** For OpenClaw/Lobo-specific structure, see `references/openclaw-lobo-workspace.md`.
**Reference:** For Hermes cron setup from scripts, see `references/hermes-cron-from-scripts.md`.

**Key files to identify and adopt:**
- `SOUL.md` or `AGENTS.md` — agent persona and behavior rules
- `USER.md` or `IDENTITY.md` — user profile for memory
- `MEMORY.md` — long-term memory (tasks, projects, decisions)
- `TOOLS.md` or equivalent — local tool configs, API endpoints
- `scripts/` — automation scripts (Python, bash, etc.)
- `memory/` or `logs/` — session history, daily notes
- `.env` or `config.yaml` — API keys, tokens, credentials
- Cron/automation definitions — what runs when

**Adopt user profile and memory into Hermes memory immediately:**
```python
memory(action="add", target="user", content="...")
memory(action="add", target="memory", content="...")
```

## Phase 4: Dependency Audit — What's Missing?

### Python Dependencies

```bash
cd <workspace>/scripts
grep -h "^import\|^from" *.py | sort | uniq
# Install missing packages
```

Common agent workspace deps:
- `google-genai`, `google-generativeai` — Gemini API
- `google-auth-oauthlib`, `google-api-python-client` — Gmail, Calendar
- `openai` — OpenAI API
- `requests` — Generic HTTP

### Hardcoded Paths

Scripts from containerized deployments often have hardcoded paths that need rewiring:

```bash
grep -rn "/data/" scripts/*.py
# Look for patterns like:
# /data/.openclaw/workspace — old container workspace
# /data/projects — old project directory
# /data/.openclaw/config — old config directory
```

**Decision:** Match the old paths or migrate the workspace to standard locations?

| Old Path | Standard Hermes Path | Notes |
|----------|---------------------|-------|
| `/data/.openclaw/workspace` | `/data/lobo` or user's preference | Create symlink for backwards compat |
| `/data/.openclaw/config` | `/data/.openclaw/config` | Keep if scripts reference it |
| `/data/projects` | `/data/projects` | Standard dev directory |

### API Keys and Secrets

The `.env` file is likely missing (`.gitignore` excludes it). Check:

```bash
ls -la <workspace>/.env <workspace>/.openclaw/.env 2>/dev/null
grep -rn "GEMINI_API_KEY\|OPENAI_API_KEY\|NOTION_TOKEN\|FIGMA_TOKEN\|BILLING" scripts/
```

**Ask the user for missing keys.** Do not guess or leave scripts broken.

**Reference:** If a script calls a third-party API with no obvious balance/status endpoint, see `references/api-endpoint-discovery.md` for the probe pattern.

## Phase 5: Workspace Setup

### Create Directory Structure

```bash
mkdir -p /data/.openclaw/workspace /data/.openclaw/config /data/projects
cp -r <repo>/* /data/.openclaw/workspace/
ln -sf /data/.openclaw/workspace /data/lobo  # convenience symlink
```

### Fix Script Paths (if needed)

If scripts reference old container paths, patch them:

```bash
sed -i 's|/data/.openclaw/workspace|/data/lobo|g' scripts/*.py
```

### Install Dependencies

```bash
pip install <missing-packages>
```

## Phase 6: Automation Migration — Cron Jobs

The old deployment likely had cron jobs. Sources to check:
- `crontab -l` on the server
- `/etc/cron.d/*` files
- The agent's `MEMORY.md` or `HEARTBEAT.md` (lists cron jobs)
- Any `jobs.json` or equivalent config file

**Reference:** For the exact Hermes cron setup pattern, see `references/hermes-cron-from-scripts.md`.

**CRITICAL: Verify user's timezone before scheduling.**

Server time is UTC. The user's local time may differ. Before setting any cron schedule:

```bash
# Check server time
date -u  # UTC
date     # server local (often also UTC)

# Ask the user their timezone and current local time
# Do NOT assume based on old memory — users move
```

Convert user-local time to UTC for the cron schedule. Costa Rica = UTC-6 (no DST). Mexico City CST = UTC-6 (standard) or UTC-5 (DST). Always confirm.

**Migrate to Hermes cron:**

```bash
hermes cron list
hermes cron create --name "daily-health-check" --schedule "0 14 * * *" --prompt "..."
```

See `cronjob` tool for creating/scheduling. The cron should point to the new script paths.

**Note on AI-driven automations:** Some legacy agent platforms ran reviews via LLM prompts rather than scripts. If MEMORY.md references a "Daily Workspace Review" but no `workspace_review.py` exists, you must **create the script from scratch** based on what the review should check (stale files, git status, memory backlog, etc.).

## Phase 7: Verification

### Basic Health Checks

```bash
# Can scripts import their deps?
python3 -c "import google.genai; import openai; print('ok')"

# Can scripts find their paths?
python3 scripts/health_check.py --help 2>&1 | head -5

# Do API keys work?
python3 -c "import os; print('GEMINI_API_KEY:', 'yes' if os.getenv('GEMINI_API_KEY') else 'no')"
```

### Functional Tests

Run each key script with dry-run or `--help` first:
- `security_review.py` — no external deps, good first test
- `health_check.py` — may need workspace state
- Gmail scripts — need Google API token
- Image/video generation — need Gemini API key

## Pitfalls

### Stale `gh` Tokens Block Device Flow
If `gh auth status` shows an invalid token for the target account, device flow will authorize but not persist. **SSH keys are the reliable fallback.**

### Missing `.env` Files Are Silent Failures
Scripts with `os.environ.get("GEMINI_API_KEY")` return `None` silently. Always verify env vars are set before running.

### Hardcoded `/data/` Paths From Container Deployments
Container workspaces mount host directories. Scripts assume `/data/` exists. On bare-metal or different hosts, create the directory structure or patch scripts.

### GitHub Private Repos Need Active Auth
Do not assume the repo is accessible. Verify with `curl -I` or `git ls-remote` before attempting clone.

### Interactive Automations Cannot Be Fully Cron-ized

Some legacy automations require **user input** mid-flow. Example: a "6 PM billing check-in" that asks "How many hours did you work today?" and waits for the user's reply before logging to an API.

**The limitation:** Hermes cron jobs deliver outbound messages but cannot hold state to process the reply in the same run. The reply comes back as a new message to the main agent session.

**Options when migrating interactive automations:**
1. **Simplify to a reminder cron** — Fire at 6 PM: "Don't forget to log hours." User handles it manually.
2. **Two-part flow** — Cron sends the prompt. Main agent (in regular chat) catches the reply and makes the API call.
3. **Fully automate if possible** — If the data source exists without user input (e.g., fetch hours from a time-tracker API), rewrite the script to be non-interactive.

Assess the old automation's **data dependency** before deciding. If it truly needs the user's brain, option 1 or 2 is correct. Do not promise full automation for inherently interactive workflows.

### Cron Jobs Reference Old Paths
If `/etc/cron.d/` has jobs pointing to `/docker/openclaw-mejc/`, they will silently fail. Audit and migrate all cron entries.

### Post-Migration Cleanup: Scripts Flag New Workspace
After copying the repo to the new workspace path, scripts like `security_review.py` may flag the new location for missing `.gitignore`, world-readable files, or other issues that were acceptable in the repo but are not acceptable in the live workspace. **Run the security and health scripts immediately after migration** and fix any findings — this validates the migration is clean.

### Memory Is Not Automatic
The agent's persona (SOUL.md), user profile (USER.md), and long-term memory (MEMORY.md) must be manually adopted into the new system's memory. They don't transfer automatically.

## Workflow Preference: Act First, Report After

The user prefers **execution over permission-seeking** for routine maintenance tasks. When the migration involves:
- Fixing `.gitignore` entries
- Installing missing Python packages
- Rewriting hardcoded paths
- Running security/health checks to validate the migration

**Do it, then report what you did.** Do not ask "Should I fix the .gitignore?" or "Can I install these packages?" Just fix it, run the check, and give a concise summary of actions taken.

Reserve asking for permission only for:
- Destructive external actions (sending emails, tweets, public posts)
- Irreversible deletions
- Spending real money

## Workflow Preference: Pivot Early

When a presentation or auth approach encounters repeated friction (QR codes not rendering, device flow timing out, token not persisting), **pivot to a simpler alternative immediately** rather than iterating on the broken approach. Users prefer a working text-based or SSH-based solution over a theoretically elegant but practically broken visual or browser flow.
