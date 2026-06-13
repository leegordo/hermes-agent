# Hermes Cron Setup from Existing Scripts

When migrating automations from another platform (OpenClaw, cron.d, etc.) to Hermes, the pattern is:

1. **Read and test the script**
2. **Write a wrapper shell script**
3. **Create the cron job via `cronjob` tool**
4. **Verify the schedule and next run**

## Step 1: Read and Test

```bash
cd /data/.openclaw/workspace
python3 scripts/security_review.py 2>&1
```

Fix any path or dependency issues before scheduling.

## Step 2: Write Wrapper Script

Create a bash wrapper in `~/.hermes/scripts/`:

```bash
#!/usr/bin/env bash
set -euo pipefail

cd /data/.openclaw/workspace
python3 scripts/security_review.py
```

Make it executable:
```bash
chmod +x ~/.hermes/scripts/security_review.sh
```

**Why a wrapper?** The `cronjob` tool's `script=` parameter expects a path relative to `~/.hermes/scripts/`. The wrapper handles `cd`, env setup, and error exits.

## Step 3: Create Cron Job

```python
cronjob(
    action='create',
    name='nightly-security-review',
    no_agent=True,          # Skip LLM — just run the script
    schedule='30 9 * * *',  # UTC cron expression
    script='security_review.sh',
)
```

**Timezone note:** Server is UTC. Convert user-local time to UTC before passing `schedule`.

**`no_agent=True`** for scripts that produce their own output. The script's stdout is delivered verbatim to the user. Use `no_agent=False` only if you want the LLM to interpret the script output and rephrase it.

## Step 4: Verify

```python
cronjob(action='list')
```

Check `next_run_at` is what you expect. If it's wrong, you calculated UTC offset incorrectly.

## Common Schedules (Costa Rica, UTC-6)

| Local (CR) | UTC | Cron |
|------------|-----|------|
| 3:30 AM | 9:30 AM | `30 9 * * *` |
| 8:00 AM | 2:00 PM | `0 14 * * *` |
| 9:00 AM | 3:00 PM | `0 15 * * *` |
| 6:00 PM | 12:00 AM+1 | `0 0 * * *` |

## Pitfall: Script Produces No Output

If the script exits 0 with empty stdout, the cron delivers **silence** — the user sees nothing. Ensure scripts print a status report, even on success:

```python
print("✅ All checks passed")
```
