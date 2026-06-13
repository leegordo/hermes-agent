#!/usr/bin/env bash
# signal_health.sh — functional watchdog for signal-cli + Hermes Signal path.
#
# Checks liveness (systemd + JSON-RPC), message-processing health (NPE signature),
# and gateway SSE freshness. Restarts signal-cli on failure; alerts out-of-band
# when recovery fails or restarts repeat too often.
#
# Tunables (env, optional overrides in ~/.hermes/.env):
#   SIGNAL_HTTP_URL          default: http://127.0.0.1:8080
#   SIGNAL_NPE_WINDOW_SEC    default: 900 (15m)
#   SIGNAL_SSE_IDLE_MAX_SEC  default: 300 (5m without inbound or connected SSE)
#   SIGNAL_RESTART_WINDOW    default: 3600 (1h)
#   SIGNAL_RESTART_MAX       default: 3 restarts/hour before alert
#   NTFY_TOPIC               optional: ntfy.sh topic for out-of-band alerts
#   NTFY_SERVER              default: https://ntfy.sh

set -uo pipefail

HERMES_HOME="${HERMES_HOME:-/root/.hermes}"
ENV_FILE="${HERMES_HOME}/.env"
STATE_DIR="${HERMES_HOME}/state"
ALERT_LOG="${HERMES_HOME}/logs/signal-alerts.log"
GATEWAY_LOG="${HERMES_HOME}/logs/gateway.log"
SIGNAL_DATA="${SIGNAL_HOME:-/root/.local/share/signal-cli/data}"
SIGNAL_HTTP_URL="${SIGNAL_HTTP_URL:-http://127.0.0.1:8080}"
NPE_WINDOW_SEC="${SIGNAL_NPE_WINDOW_SEC:-900}"
SSE_IDLE_MAX_SEC="${SIGNAL_SSE_IDLE_MAX_SEC:-300}"
RESTART_WINDOW_SEC="${SIGNAL_RESTART_WINDOW:-3600}"
RESTART_MAX="${SIGNAL_RESTART_MAX:-3}"
NTFY_SERVER="${NTFY_SERVER:-https://ntfy.sh}"

if [[ -f "$ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  set -a
  source "$ENV_FILE"
  set +a
fi

mkdir -p "$STATE_DIR" "$(dirname "$ALERT_LOG")"
RESTART_STATE="${STATE_DIR}/signal-health-restarts.json"
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

pass=0
fail=0
actions=()
issues=()

pass_check() { pass=$((pass + 1)); }
fail_check() { fail=$((fail + 1)); issues+=("$1"); }

log() { echo "[$TS] $*" | tee -a "$ALERT_LOG"; }

send_alert() {
  local msg="$1"
  log "ALERT: $msg"
  if [[ -n "${NTFY_TOPIC:-}" ]]; then
    curl -fsS -m 10 \
      -H "Title: Hermes Signal alert" \
      -H "Priority: high" \
      -H "Tags: warning,hermes,signal" \
      -d "$msg" \
      "${NTFY_SERVER}/${NTFY_TOPIC}" >/dev/null 2>&1 || true
  fi
}

record_restart() {
  python3 - <<'PY' "$RESTART_STATE" "$RESTART_WINDOW_SEC"
import json, sys, time
from pathlib import Path

path = Path(sys.argv[1])
window = int(sys.argv[2])
now = int(time.time())
data = {"timestamps": []}
if path.exists():
    try:
        data = json.loads(path.read_text())
    except Exception:
        pass
data["timestamps"] = [t for t in data.get("timestamps", []) if now - t <= window]
data["timestamps"].append(now)
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(data, indent=2))
print(len(data["timestamps"]))
PY
}

kill_orphan_signal_cli() {
  local pids=""
  if command -v lsof >/dev/null 2>&1 && [[ -e "$SIGNAL_DATA" ]]; then
    pids=$(lsof -t "$SIGNAL_DATA" 2>/dev/null | sort -u || true)
  fi
  if [[ -z "$pids" ]]; then
    pids=$(pgrep -f '/opt/signal-cli/.*/bin/signal-cli daemon' 2>/dev/null || true)
  fi
  if [[ -n "$pids" ]] && ! systemctl is-active --quiet signal-cli.service 2>/dev/null; then
    log "Killing orphaned signal-cli process(es): $pids"
    # shellcheck disable=SC2086
    kill -9 $pids 2>/dev/null || true
    actions+=("killed-orphan")
    sleep 2
  fi
}

restart_signal_cli() {
  kill_orphan_signal_cli
  log "Restarting signal-cli.service"
  systemctl restart signal-cli.service
  actions+=("restarted-signal-cli")
  local count
  count=$(record_restart)
  if (( count > RESTART_MAX )); then
    send_alert "signal-cli restarted ${count} times in ${RESTART_WINDOW_SEC}s — investigate upstream or config lock"
  fi
  sleep 3
}

# --- checks ---

if systemctl is-active --quiet signal-cli.service; then
  pass_check
else
  fail_check "signal-cli.service inactive"
fi

rpc_ok=0
rpc_body="$(curl -fsS -m 5 "${SIGNAL_HTTP_URL}/api/v1/rpc" \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","method":"listAccounts","id":1}' 2>/dev/null || true)"
if echo "$rpc_body" | grep -q '"result"'; then
  pass_check
  rpc_ok=1
else
  fail_check "signal-cli JSON-RPC listAccounts failed"
fi

npe_count=0
if journalctl -u signal-cli.service --since "${NPE_WINDOW_SEC} sec ago" --no-pager 2>/dev/null \
  | grep -q 'getServerGuid(...) must not be null'; then
  npe_count=1
  fail_check "signal-cli NPE (getServerGuid) in last ${NPE_WINDOW_SEC}s — upgrade needed"
fi

sse_ok=0
if [[ -f "$GATEWAY_LOG" ]]; then
  last_inbound="$(grep 'inbound message: platform=signal' "$GATEWAY_LOG" 2>/dev/null | tail -1 | awk '{print $1, $2}' || true)"
  last_sse="$(grep 'Signal SSE' "$GATEWAY_LOG" 2>/dev/null | tail -1 || true)"
  now_epoch="$(date +%s)"

  if [[ -n "$last_inbound" ]]; then
    inbound_epoch="$(date -d "$last_inbound" +%s 2>/dev/null || echo 0)"
    if (( now_epoch - inbound_epoch <= SSE_IDLE_MAX_SEC )); then
      sse_ok=1
      pass_check
    fi
  fi

  if (( sse_ok == 0 )) && echo "$last_sse" | grep -qi 'connected'; then
    sse_ok=1
    pass_check
  fi

  if (( sse_ok == 0 )); then
    fail_check "gateway Signal path stale (no recent inbound / SSE not connected)"
  fi
else
  fail_check "gateway.log missing"
fi

if systemctl is-active --quiet hermes-gateway.service; then
  pass_check
else
  fail_check "hermes-gateway.service inactive"
fi

# --- recovery ---

if (( fail > 0 )); then
  if (( rpc_ok == 0 )) || ! systemctl is-active --quiet signal-cli.service || (( npe_count > 0 )); then
    restart_signal_cli
    # Re-check RPC after restart
    rpc_body="$(curl -fsS -m 5 "${SIGNAL_HTTP_URL}/api/v1/rpc" \
      -H 'Content-Type: application/json' \
      -d '{"jsonrpc":"2.0","method":"listAccounts","id":2}' 2>/dev/null || true)"
    if ! echo "$rpc_body" | grep -q '"result"'; then
      send_alert "signal-cli recovery failed after restart. Issues: $(IFS='; '; echo "${issues[*]}")"
      echo "SIGNAL_HEALTH FAIL recovered=no issues=${issues[*]} actions=${actions[*]:-none} ts=${TS}"
      exit 1
    fi
  fi

  if ! systemctl is-active --quiet hermes-gateway.service; then
    log "Restarting hermes-gateway.service"
    systemctl restart hermes-gateway.service
    actions+=("restarted-hermes-gateway")
  fi
fi

if (( fail > 0 )); then
  send_alert "Signal health check had issues (${issues[*]}) — actions: ${actions[*]:-none}"
  echo "SIGNAL_HEALTH FAIL recovered=partial issues=${issues[*]} actions=${actions[*]:-none} ts=${TS}"
  exit 1
fi

echo "SIGNAL_HEALTH OK checks=${pass} ts=${TS}"
exit 0
