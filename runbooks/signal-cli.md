# Signal CLI Runbook

Last updated: 2026-06-12

## Architecture

- **signal-cli daemon**: `signal-cli.service` → HTTP on `127.0.0.1:8080`
- **Hermes gateway**: `hermes-gateway.service` → SSE to `/api/v1/events`
- **Binary**: `/opt/signal-cli/signal-cli-0.14.5/bin/signal-cli`
- **Symlink**: `/usr/local/bin/signal-cli`
- **Data**: `/root/.local/share/signal-cli/`
- **Watchdog**: `signal-health.timer` (every 2 min) → `~/.hermes/scripts/signal_health.sh`
- **Alerts**: `~/.hermes/logs/signal-alerts.log`; optional `NTFY_TOPIC` in `~/.hermes/.env`

## Quick status

```bash
systemctl status signal-cli hermes-gateway signal-health.timer
curl -s http://127.0.0.1:8080/api/v1/rpc \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","method":"listAccounts","id":1}'
journalctl -u signal-cli -n 30 --no-pager
grep 'Signal SSE\|inbound message: platform=signal' ~/.hermes/logs/gateway.log | tail -5
```

## Restart (normal)

```bash
systemctl restart signal-cli
sleep 3
curl -s http://127.0.0.1:8080/api/v1/rpc \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","method":"listAccounts","id":1}'
systemctl restart hermes-gateway
```

## Orphan process / config lock

Symptom: `systemctl status signal-cli` shows **inactive (dead)** but a process still holds the data dir, or logs say *"Config file is in use by another instance, waiting..."*.

```bash
lsof /root/.local/share/signal-cli/data
pgrep -af 'signal-cli daemon'
# kill orphaned PIDs, then:
systemctl restart signal-cli
```

## NPE: getServerGuid(...) must not be null

Symptom: inbound messages stop processing; journal shows `Envelope from: unknown source (device: 0)` + NPE.

**Fix:** upgrade signal-cli from [AsamK/signal-cli releases](https://github.com/AsamK/signal-cli/releases) (native Linux tarball):

```bash
systemctl stop signal-cli
# kill any orphan as above
mkdir -p /opt/signal-cli/signal-cli-<VERSION>/bin
tar -xzf signal-cli-<VERSION>-Linux-native.tar.gz -C /opt/signal-cli/signal-cli-<VERSION>/bin signal-cli
chmod +x /opt/signal-cli/signal-cli-<VERSION>/bin/signal-cli
# update ExecStart in /etc/systemd/system/signal-cli.service
ln -sf /opt/signal-cli/signal-cli-<VERSION>/bin/signal-cli /usr/local/bin/signal-cli
systemctl daemon-reload
systemctl start signal-cli
systemctl restart hermes-gateway
```

## Never do this

- Do **not** start `signal-cli daemon` from an SSH session or terminal — it dies when the session ends.
- Always use `signal-cli.service` (or `systemd-run` with a unit).

## Out-of-band alerting

Add to `~/.hermes/.env`:

```
NTFY_TOPIC=your-secret-topic-name
# optional: NTFY_SERVER=https://ntfy.sh
```

Subscribe on your phone via the ntfy app. The watchdog sends alerts when recovery fails or restarts exceed 3/hour.

## MemPalace reference

Drawer: `user-notes/infrastructure-issues` → `f4ef416031de4f61c65a0ba5`
