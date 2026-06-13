---
name: cursor-agent
description: "Delegate coding and exploration to Cursor Agent CLI (subagents, parallel work)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Coding-Agent, Cursor, Subagent, Delegation, Code-Review, Refactoring]
    related_skills: [claude-code, codex, opencode, subagent-driven-development, hermes-agent]
---

# Cursor Agent — Hermes Orchestration Guide

Delegate work to [Cursor Agent](https://cursor.com/docs) on this VPS via the `agent` CLI (`/root/.local/bin/agent`). Cursor runs with its own tools (edit, terminal, MCP, nested subagents) in an isolated workspace — Hermes stays the orchestrator and only sees the final result.

## Three delegation layers (pick deliberately)

| Layer | Mechanism | Best for |
|-------|-----------|----------|
| **Hermes `delegate_task`** | Built-in subagents, same model stack | Quick parallel tasks, reviews, web research, bounded toolsets |
| **Cursor `agent -p`** (this skill) | Full Cursor agent + `@subagent` routing | Heavy coding, MCP-rich work, Cursor skills/rules, design-to-code |
| **Hermes `hermes chat -q`** | Separate Hermes process | Long multi-hour missions, Signal/cron delivery |

**Rule:** Use `delegate_task` for Hermes-native subtasks. Use **this skill** when the user asks for Cursor, when you need Cursor MCP/plugins, or when implementation should run in Cursor's agent loop (including Cursor subagents under `~/.cursor/agents/`).

## Prerequisites on this VPS

- **CLI:** `agent` at `/root/.local/bin/agent` (cursor-agent package, currently `2026.01.28-fd13201`)
- **Headless auth (required for `-p`):** `CURSOR_API_KEY` in `~/.hermes/.env`
  - Create at [Cursor Dashboard → Integrations](https://cursor.com/dashboard/integrations)
  - OAuth via `agent login` works for interactive/TUI only — **print mode rejects OAuth-only sessions**
- **Verify:**
  ```
  python3 ~/.hermes/scripts/cursor_delegate.py --check
  ```
- **Custom subagents:** `~/.cursor/agents/*.md` (bundled with this setup: `explore`, `shell-runner`, `code-implementer`, `code-reviewer`)

## Preferred: helper script (loads `.env` safely)

Avoid hand-rolling `agent` flags; use the wrapper so `CURSOR_API_KEY` is always loaded (`.env` may contain characters that break shell `source`).

### One-shot task

```
terminal(
  command='python3 ~/.hermes/scripts/cursor_delegate.py --workspace ~/Projects/myapp --goal "Implement JWT refresh in src/auth/" --context "Use existing session store in src/session.py. Run pytest tests/auth/ when done." --timeout 900',
  timeout=920
)
```

### Invoke a named Cursor subagent

Subagents live in `~/.cursor/agents/`. Reference them with `@name` in the goal (Cursor routes automatically):

```
terminal(
  command='python3 ~/.hermes/scripts/cursor_delegate.py --workspace ~/Projects/myapp --subagent explore --goal "Map how cron jobs are registered and list all entrypoints" --timeout 600',
  timeout=620
)
```

| `--subagent` | Maps to | Use when |
|--------------|---------|----------|
| `explore` | `@explore` | Read-only codebase discovery, architecture questions |
| `shell` | `@shell-runner` | Git, builds, deploy scripts, command sequences |
| `implementer` | `@code-implementer` | Feature implementation with tests |
| `reviewer` | `@code-reviewer` | Spec/security review after changes |

### Parallel Cursor workers (Hermes orchestrator pattern)

Match `subagent-driven-development`: partition directories, run workers in background, merge after.

```
# Worker A — committee section only
terminal(
  command='python3 ~/.hermes/scripts/cursor_delegate.py --workspace ~/Projects/0xcreative --subagent implementer --goal "Build committee/index.html only under committee/. Use shared CSS at assets/css/0xcreative.css. Do not edit other sections." --timeout 1200',
  background=true
)

# Worker B — blog section only
terminal(
  command='python3 ~/.hermes/scripts/cursor_delegate.py --workspace ~/Projects/0xcreative --subagent implementer --goal "Build blog/index.html only under blog/. Shared CSS at assets/css/0xcreative.css." --timeout 1200',
  background=true
)

# Poll both, then inspect filesystem and summarize for the user
process(action="poll", session_id="<id_a>")
process(action="poll", session_id="<id_b>")
```

Cap parallel Cursor jobs at **2–3** (same discipline as `delegation.max_concurrent_children`).

## Direct `agent` CLI (when not using the wrapper)

Print mode flags Hermes should remember:

```
agent -p "TASK PROMPT" \
  --workspace /path/to/project \
  --output-format json \
  --force \
  --approve-mcps
```

| Flag | Effect |
|------|--------|
| `-p` / `--print` | Non-interactive; exits with result (required for Hermes) |
| `--workspace <path>` | Project root (defaults to CWD) |
| `--output-format json` | Structured result for parsing |
| `--force` | Auto-approve commands (VPS / trusted environments) |
| `--approve-mcps` | Auto-approve MCP servers in headless mode |
| `--model <id>` | Override model when needed |
| `--mode plan` | Read-only planning pass |
| `--continue` / `--resume <id>` | Multi-turn continuation |
| `-c` / `--cloud` | Cloud VM run (repo clone); use when local disk is wrong |

**Environment:** Export `CURSOR_API_KEY` or rely on the wrapper. Do not assume `agent login` alone enables `-p`.

### Example: PR-style review

```
terminal(
  command='cd ~/Projects/myapp && agent -p "Review git diff against main for security and correctness. Output: Critical / Important / Minor / Verdict." --output-format json --force --approve-mcps',
  timeout=300
)
```

Parse JSON: look for the assistant result text in the response payload (schema varies by CLI version; prefer the wrapper which normalizes output).

## Pairing with `subagent-driven-development`

Use Hermes as the **orchestrator** and Cursor as **implementer/reviewer** workers:

1. Hermes reads the plan once and maintains the todo list.
2. Per task, call `cursor_delegate.py --subagent implementer` with **full task text in `--goal` and `--context`** (never "read the plan file").
3. After each task, `--subagent reviewer` with file paths and original spec.
4. Hermes marks todos complete and runs integration checks.

Hermes `delegate_task` remains valid for lightweight reviewers or web-only research; Cursor is for repo edits at scale.

## Context contract (same as `delegate_task`)

Cursor subagents start with **zero** Hermes conversation history. Every call must include:

- Exact file paths and repo root (`--workspace`)
- Acceptance criteria and test commands
- What **not** to touch (directory contracts for parallel runs)
- Prior subagent output summaries when chaining work

```python
# BAD
cursor_delegate.py --goal "Fix the bug"

# GOOD
cursor_delegate.py --workspace ~/Projects/api --goal "Fix NoneType in process_request" --context "Error on api/handlers.py:47 when Content-Type missing. parse_body() returns None. Add guard + test in tests/test_handlers.py."
```

## Recovery: timeouts and partial output

Default wrapper timeout is 900s. Creative/HTML tasks may need `--timeout 1800` or smaller scoped goals.

On timeout:

1. Inspect the workspace for files written.
2. If >70% complete, dispatch a follow-up Cursor job with **only** the remaining scope.
3. Never discard partial work without reading it.

## When to use Cursor vs Claude Code / Codex

| Prefer Cursor (`agent`) | Prefer Claude Code / Codex |
|-------------------------|----------------------------|
| User says "use Cursor" | User names Claude Code or Codex |
| Need Cursor MCP plugins (Figma, etc.) | Anthropic/OpenAI-specific CLIs already configured |
| Project has `.cursor/rules` or `.cursor/agents` | Project is Claude/Codex-native |
| Design work tied to Cursor skills on this server | One-shot without Cursor API key |

## Pitfalls

1. **`-p` without `CURSOR_API_KEY`** → immediate auth error (OAuth login does not fix print mode).
2. **Missing `--workspace`** → agent runs in wrong CWD; edits land in unexpected paths.
3. **Parallel workers without directory contracts** → merge conflicts (see `subagent-driven-development` parallel contract reference).
4. **Oversized goals** → timeout; split into implementer-sized tasks (2–5 minutes of focused work each).
5. **`--force` on untrusted prompts** → treat like `delegation.subagent_auto_approve: true`; only on this trusted VPS.

## Further reading

- `references/hermes-vs-cursor-matrix.md` — decision matrix and auth troubleshooting
- Cursor subagent format: `~/.cursor/agents/` and Cursor docs on custom agents
- Hermes: `subagent-driven-development` skill for orchestration discipline
