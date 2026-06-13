#!/usr/bin/env python3
"""
Run Cursor Agent CLI in headless mode for Hermes orchestration.

Loads CURSOR_API_KEY from ~/.hermes/.env without shell sourcing (safe for special chars).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

HERMES_ENV = Path.home() / ".hermes" / ".env"
AGENT_BIN = Path("/root/.local/bin/agent")

SUBAGENT_ALIASES = {
    "explore": "explore",
    "shell": "shell-runner",
    "shell-runner": "shell-runner",
    "implementer": "code-implementer",
    "code-implementer": "code-implementer",
    "reviewer": "code-reviewer",
    "code-reviewer": "code-reviewer",
}


def load_dotenv(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.is_file():
        return out
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1]
        out[key] = val
    return out


def build_prompt(goal: str, context: str | None, subagent: str | None) -> str:
    parts: list[str] = []
    if subagent:
        name = SUBAGENT_ALIASES.get(subagent, subagent)
        parts.append(f"Use @{name} for this task.")
    parts.append(goal.strip())
    if context and context.strip():
        parts.append("\n\nCONTEXT:\n" + context.strip())
    parts.append(
        "\n\nWhen finished, reply with a structured summary: "
        "Done / Files changed / Commands run / Tests / Blockers."
    )
    return "\n".join(parts)


def run_agent(
    *,
    workspace: Path,
    prompt: str,
    timeout: int,
    model: str | None,
    plan_mode: bool,
    env: dict[str, str],
) -> dict[str, Any]:
    cmd = [
        str(AGENT_BIN),
        "-p",
        prompt,
        "--workspace",
        str(workspace.resolve()),
        "--output-format",
        "json",
        "--force",
        "--approve-mcps",
    ]
    if model:
        cmd.extend(["--model", model])
    if plan_mode:
        cmd.append("--plan")

    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
        cwd=str(workspace.resolve()),
    )
    result: dict[str, Any] = {
        "exit_code": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }
    if proc.stdout.strip():
        try:
            result["json"] = json.loads(proc.stdout)
        except json.JSONDecodeError:
            result["json"] = None
    return result


def cmd_check(env: dict[str, str]) -> int:
    key = env.get("CURSOR_API_KEY", "")
    print(f"agent binary: {AGENT_BIN} ({'ok' if AGENT_BIN.is_file() else 'MISSING'})")
    print(f"CURSOR_API_KEY: {'set' if key else 'NOT SET (required for -p)'}")
    print(f"~/.cursor/agents: {list((Path.home() / '.cursor' / 'agents').glob('*.md'))}")
    if not key:
        print("\nAdd CURSOR_API_KEY to ~/.hermes/.env — see cursor-agent skill.", file=sys.stderr)
        return 1
    try:
        proc = subprocess.run(
            [str(AGENT_BIN), "-p", "Reply with exactly: CURSOR_OK"],
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
            cwd="/tmp",
        )
    except subprocess.TimeoutExpired:
        print("probe: TIMEOUT", file=sys.stderr)
        return 1
    if proc.returncode != 0:
        print("probe failed:", proc.stderr or proc.stdout, file=sys.stderr)
        return 1
    print("probe: ok")
    if "CURSOR_OK" in (proc.stdout or ""):
        print("response contains CURSOR_OK")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Delegate a task to Cursor Agent CLI")
    parser.add_argument("--check", action="store_true", help="Verify auth and binary")
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--goal", type=str, default="")
    parser.add_argument("--context", type=str, default="")
    parser.add_argument("--subagent", type=str, default="", choices=[""] + sorted(SUBAGENT_ALIASES.keys()))
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--model", type=str, default="")
    parser.add_argument("--plan", action="store_true")
    args = parser.parse_args()

    dotenv = load_dotenv(HERMES_ENV)
    env = os.environ.copy()
    for k, v in dotenv.items():
        if k not in env or not env[k]:
            env[k] = v

    if args.check:
        return cmd_check(env)

    if not args.goal.strip():
        parser.error("--goal is required unless using --check")
    if not env.get("CURSOR_API_KEY"):
        print("CURSOR_API_KEY not set in ~/.hermes/.env", file=sys.stderr)
        return 1
    if not AGENT_BIN.is_file():
        print(f"agent CLI not found at {AGENT_BIN}", file=sys.stderr)
        return 1

    workspace = args.workspace.expanduser().resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    prompt = build_prompt(args.goal, args.context or None, args.subagent or None)
    out = run_agent(
        workspace=workspace,
        prompt=prompt,
        timeout=args.timeout,
        model=args.model or None,
        plan_mode=args.plan,
        env=env,
    )
    print(json.dumps(out, indent=2))
    return 0 if out["exit_code"] == 0 else out["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
