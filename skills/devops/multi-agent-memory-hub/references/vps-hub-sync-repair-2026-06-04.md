# Session Log: VPS Hub Sync Repair (2026-06-04)

## Symptoms Reported
- Claude Code on Mac detected VPS hub had never pushed a sync commit
- `manifest.json` showed `"last_export": null` for `mempalace-vps-hub`
- User asked Hermes to investigate and fix

## Root Causes Found

### 1. Git remote URL contained a dead token
The repo was cloned with an embedded PAT in the URL:
```
https://github...bXTL@github.com/leegordo/multi-agent-memory.git
```
Every fetch/push failed with:
```
fatal: could not read Password for 'https://github...bXTL@github.com': No such device or address
```
**Fix:** Strip the token from the URL and rely on the credential helper:
```bash
git remote set-url origin https://github.com/<user>/<repo>.git
```
The VPS had `git config --global credential.helper store` and `~/.git-credentials` with a valid token, so clean HTTPS worked.

### 2. seed-mempalace.py passed invalid keys to mempalace_kg_add
The `kg_add` tool schema only accepts:
- `subject`, `predicate`, `object` (required)
- `valid_from`, `valid_to` (optional)
- `source_closet`, `source_file`, `source_drawer_id` (optional)

The seed script was passing `id`, `name`, `type`, `source` from `entities.jsonl` records, causing:
```
[seed] kg_add failed: RPC error on tools/call: {'code': -32000, 'message': 'Internal tool error'}
```
**Fix:** Strip extra keys before calling `kg_add`. Also, `entities.jsonl` records don't have SPO (subject/predicate/object) — only `observations.jsonl` does. Entity-only records should be skipped.

Patch applied to `scripts/seed-mempalace.py`:
```python
def _strip_extra_keys(obj: dict) -> dict:
    allowed = {"subject", "predicate", "object", "valid_from", "valid_to",
               "source_closet", "source_file", "source_drawer_id"}
    return {k: v for k, v in obj.items() if k in allowed}
```

### 3. export.py only updated the Mac consumer's last_export
The `update_manifest()` function in `adapters/mempalace/export.py` only matched `consumer.get("name") == "mempalace"`, so the VPS hub's `last_export` stayed `null`.

**Fix:** Prioritize the `mempalace-vps-hub` consumer:
```python
hub_updated = False
for consumer in data.get("consumers", []):
    if consumer.get("name") == "mempalace-vps-hub":
        consumer["last_export"] = utc_now()
        hub_updated = True
        break
if not hub_updated:
    # fallback to legacy mempalace consumer
    ...
```

### 4. systemd user sessions unavailable on this VPS
`systemctl --user` fails with:
```
Failed to connect to bus: No medium found
```
The `bootstrap-hermes.sh` script's systemd timer path doesn't work here.

**Fix:** Use Hermes cron (`cronjob` tool) as the automation fallback:
```
cronjob create --schedule "*/15 * * * *" --workdir /root/Projects/multi-agent-memory
```

## Verification Steps

After fixes, a clean `hub-sync.sh` run produced:
```
[hub-sync srv1354161 02:19:28Z] git sync (pull/rebase/push local commits)
[sync srv1354161 02:19:29Z] sync ok
[hub-sync srv1354161 02:19:29Z] seed repo → palace
[seed] done. report: {"imported": 0, "updated": 0, "skipped_ledger": 53, "defaulted": 0, "failed": 0}
[hub-sync srv1354161 02:19:31Z] export palace → repo
[export] done. {"drawers": 18, "tunnels": 0, "kg_entities": 15, "kg_observations": 19, "failed": 0}
[main b5ab03f] hub: export from srv1354161 @ 20260604T021932Z
```

Zero failures. First VPS export commit in git history.

## Files Modified
- `scripts/seed-mempalace.py` — strip extra keys for kg_add, skip entity-only records
- `adapters/mempalace/export.py` — prioritize mempalace-vps-hub consumer in manifest
- `.gitignore` — exclude `*.conflict*.md` and `__pycache__`
- `memory/manifest.json` — updated last_export for VPS hub
