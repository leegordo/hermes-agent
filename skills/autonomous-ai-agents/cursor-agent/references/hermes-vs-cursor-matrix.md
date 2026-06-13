# Hermes vs Cursor delegation matrix

## Auth troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `agent status` OK but `agent -p` fails | Print mode requires API key | Set `CURSOR_API_KEY` in `~/.hermes/.env` |
| `No models available` | Key invalid or account has no models | Regenerate key; run `agent models` with key set |
| Hermes terminal cannot find `agent` | PATH | Use full path `/root/.local/bin/agent` or wrapper script |

## Subagent type mapping (IDE → CLI via `@name`)

Cursor IDE's Task tool uses `subagent_type` (`explore`, `shell`, `generalPurpose`, …). On this VPS, Hermes maps those roles to **custom agents** in `~/.cursor/agents/` and invokes them with `@name` in the prompt:

| IDE / Hermes intent | Cursor agent file | Invocation |
|---------------------|-------------------|------------|
| explore | `explore.md` | `--subagent explore` |
| shell | `shell-runner.md` | `--subagent shell` |
| generalPurpose / implementer | `code-implementer.md` | `--subagent implementer` |
| code-reviewer | `code-reviewer.md` | `--subagent reviewer` |

Add more agents by creating `~/.cursor/agents/<name>.md` with YAML `name` + `description`, then call via `--subagent <name>` once the wrapper's alias table is extended (or pass `@<name>` directly in `--goal`).

## Cost and concurrency

- Each Cursor `-p` run is a full agent session (higher cost than a single `delegate_task` turn).
- Run at most **3** concurrent Cursor workers unless the user raises limits.
- Prefer Hermes `delegate_task` for web-only or single-file reviews.
