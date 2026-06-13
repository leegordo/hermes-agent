# Signal NPE: getServerGuid must not be null

Session context: VPS (Ubuntu 24.04), Hermes gateway, signal-cli daemon mode.
Date: 2026-06-12

## Problem

signal-cli v0.14.4.1 started throwing `Exception: getServerGuid(...) must not be null (NullPointerException)` on *every* inbound message. Messages were arriving at the daemon (receipt messages showed up) but crashing before the data payload could be read. Hermes gateway reported `signal connected` and SSE running, but no inbound text ever reached the adapter.

Log signature:
```
Exception: getServerGuid(...) must not be null (NullPointerException)
Sent by unidentified/sealed sender
Server timestamps: received: 1781236453495 ...
Timestamp: 1781236452679
Envelope from: unknown source (device: 0) to +525****3563
```

This appeared after a Signal server-side format change. signal-cli < v0.14.5 could not parse the new `serverGuid` field.

## Root causes (two in one session)

1. **signal-cli bug**: v0.14.4.1 incompatible with current Signal server format → NPE on every inbound message.
2. **Zombie process**: The old signal-cli Java process (PID 556124) had survived outside of systemd after gateway restarts, locking `~/.local/share/signal-cli/data/797835.d/account.db-*`. When `systemctl start signal-cli.service` was tried, it logged `Config file is in use by another instance, waiting…` indefinitely. `ss -tlnp` showed the port being held by the old PID, not the systemd child.

## Fix sequence

```bash
# 1. Kill the stray process
pkill -9 -f "signal-cli daemon"          # or kill -9 <PID>
sleep 2
pgrep -a signal-cli || echo "all clear"

# 2. Download and install latest native binary
# Native .tar.gz extracts a single ELF binary
cd /tmp
curl -LO https://github.com/AsamK/signal-cli/releases/download/v0.14.5/signal-cli-0.14.5-Linux-native.tar.gz
tar xzf signal-cli-0.14.5-Linux-native.tar.gz
cp /tmp/signal-cli /opt/signal-cli/signal-cli-0.14.4.1/bin/signal-cli
signal-cli --version     # → signal-cli 0.14.5

# 3. Restart systemd service
systemctl restart signal-cli.service

# 4. Verify HTTP API comes back
curl -s http://127.0.0.1:8080/api/v1/rpc \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"listAccounts","id":1}'
# → {"jsonrpc":"2.0","result":[{"number":"+525****3563"}],"id":1}

# 5. Restart Hermes gateway
hermes gateway restart
```

## Verifying it's fixed

- `journalctl -u signal-cli.service` shows clean inbound messages with `Body:` lines, no `Exception`.
- `grep signal ~/.hermes/logs/gateway.log | tail` shows `Signal SSE: connected` and inbound message entries.
- `hermes status --all` shows `Signal ✓ configured`.

## Preventive note

For native ELF builds, the embedded HTTP server uses `/api/v1/rpc` for JSON-RPC. The REST endpoints (`/v1/accounts`, etc.) that exist in the JAR distribution may not be present in the native build. Verify with JSON-RPC calls if REST returns 404.

## References

- Upstream issue: https://github.com/AsamK/signal-cli/issues (search "getServerGuid")
- Release page: https://github.com/AsamK/signal-cli/releases
