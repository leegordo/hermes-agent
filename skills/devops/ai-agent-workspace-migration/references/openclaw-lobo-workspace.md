# OpenClaw / Lobo Workspace Reference

Condensed reference for migrating an OpenClaw or Lobo-style AI agent workspace to Hermes.

## Directory Structure

```
<repo>/
├── SOUL.md              # Agent persona, behavior rules, anti-patterns
├── AGENTS.md            # Workspace rules, memory protocol, sub-agent rules
├── USER.md              # User profile (name, email, timezone, comms style)
├── IDENTITY.md          # Agent identity (name, vibe, emoji)
├── MEMORY.md            # Long-term memory: tasks, projects, decisions, cron list
├── HEARTBEAT.md         # Heartbeat checklist for proactive checks
├── TOOLS.md             # Local tool configs: API endpoints, tokens, device names
├── .gitignore           # Excludes .env, *.key, runtime/, state/
├── .openclaw/
│   └── workspace-state.json   # {"version": 1, "setupCompletedAt": "..."}
├── scripts/             # Python automation scripts
│   ├── health_check.py
│   ├── security_review.py
│   ├── workspace_review.py   # (may need to be created — was AI-driven)
│   ├── morning_committee.py
│   ├── gmail_*.py
│   ├── generate_image.py
│   ├── generate_video.py
│   ├── gemini_tts.py
│   └── usage_tracker.py
├── memory/              # Daily notes + agent prompts
│   ├── YYYY-MM-DD.md
│   ├── heartbeat-state.json
│   ├── health-state.json
│   ├── finn-prompt.md
│   ├── dieter-prompt.md
│   └── carl-prompt.md
├── projects/            # Client/project specs
│   ├── leegordondesign/
│   ├── stickergiant/
│   └── doodlehaus/
├── skills/              # Custom skills (not Hermes format)
├── tasks/               # Inbound briefs
└── billing-tool/        # Local billing tool config
```

## Key Scripts and Dependencies

| Script | Purpose | External Deps | Needs API Key |
|--------|---------|---------------|---------------|
| `health_check.py` | Disk, logs, CRM freshness, gateway binding | None | No |
| `security_review.py` | Secret scanning, permissions, gitignore | None | No |
| `workspace_review.py` | Stale files, git status, memory backlog | None | No |
| `gmail_lead_scan.py` | Gmail metadata scan for leads | google-auth, google-api-python-client | Google OAuth token |
| `gmail_mass_archive.py` | Bulk archive non-client emails | google-auth, google-api-python-client | Google OAuth token |
| `generate_image.py` | Image generation via Gemini | google-genai | GEMINI_API_KEY |
| `generate_video.py` | Video generation via Gemini | google-genai | GEMINI_API_KEY |
| `gemini_tts.py` | Text-to-speech (Charon voice) | requests | GEMINI_API_KEY |
| `morning_committee.py` | Multi-agent debate, Notion publish | openai, requests | NOTION_TOKEN, OPENAI_API_KEY |

## Cron Jobs (Typical Set)

1. **Nightly Security Review** — 3:30 AM local — `security_review.py`
2. **Daily Health Check** — 8:00 AM local — `health_check.py --level daily`
3. **Daily Workspace Review** — 9:00 AM local — `workspace_review.py`
4. **Daily Inbox Lead Scan** — 9:00 AM local — `gmail_lead_scan.py`
5. **PPQ Credit Monitor** — 10:00 AM local — (needs PPQ API key)
6. **Weekday Billing Check-in** — 6:00 PM Mon-Fri — (needs billing tool password)
7. **Monday Morning Committee** — 9:30 AM Mon — `morning_committee.py`
8. **OpenClaw Auto-Update** — 4:00 AM daily — **DEAD** (platform-specific)
9. **Weekly Hero Video** — DISABLED (expired API key)

## Path Rewiring

Old container paths → New paths:
- `/data/.openclaw/workspace` → `/data/.openclaw/workspace` (keep same, create symlink `/data/lobo`)
- `/data/.openclaw/config` → `/data/.openclaw/config`
- `/data/projects` → `/data/projects`
- `/docker/openclaw-mejc/` → **GONE** (was the Docker deployment root)

## Common Post-Migration Issues

1. **Missing `.env`** — GitHub repo excludes it. Scripts fail silently with `None` for env vars.
2. **Broken Google paths** — Gmail scripts may have literal `'/data/...json'` placeholders from redaction.
3. **Missing `workspace_review.py`** — Was AI-driven in OpenClaw; must be created as a real script.
4. **`.gitignore` gaps** — Security review flags missing entries after copy.
5. **Google token expiry** — `google_token.json` may be expired; needs re-auth via `google_auth.py`.
