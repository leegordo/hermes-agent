# Cross-Reference: Remote Static Preview

## When to Use This

When subagent-driven-development workflows produce visual artifacts (HTML mockups, design concepts, dashboards) that need user review in a real browser, use the **remote-static-preview** skill to expose them from the remote VPS.

## Quick Checklist

1. **Serve the directory** — `python3 -m http.server <PORT> --bind 0.0.0.0`
2. **Open the firewall** — `ufw allow <PORT>/tcp`
3. **Get public IP** — `curl -s icanhazip.com`
4. **Verify end-to-end** — `curl -s -o /dev/null -w "%{http_code}" http://<IP>:<PORT>/`
5. **Give user the URL** — `http://<IP>:<PORT>/`
6. **Fallback if blocked** — Use `tailscale serve` or deploy to Netlify

## Common Pitfall

Subagents may produce files but the parent agent forgets that `127.0.0.1` is localhost-only. The parent must verify `--bind 0.0.0.0` and firewall before declaring previews ready.

## Related Skills

- `devops/remote-static-preview` — Full skill with firewall, Tailscale, and Netlify workflows.
