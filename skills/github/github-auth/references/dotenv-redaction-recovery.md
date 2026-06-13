# .env Redaction Recovery — Session Reference

## Symptom

The Signal agent (or any subprocess that sources `/root/.env`) reports `401 Bad Credentials` on every GitHub API call. Meanwhile, `gh auth status` in a terminal session shows the user as fully authenticated and `gh api user` returns 200.

## Root Cause

`/root/.env` contains literal `***` instead of real token values. The tokens were redacted by a security scanner or credential-sanitization pass in a prior session. The `gh` CLI stores its OAuth token separately in `~/.config/gh/hosts.yml`, which was NOT redacted, so `gh` continues to work while `.env`-dependent code fails.

## Diagnostic Commands

```bash
# Check .env — if it shows ***, it's corrupted
cat /root/.env

# Check gh — if this works, the token is alive elsewhere
gh auth status
gh api user --jq '.login'

# Verify the disconnect: curl with .env token fails
curl -s -o /dev/null -w "%{http_code}" -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user
# Returns 401
```

## Recovery

```bash
# Extract the real token from gh's credential store
TOKEN=$(gh auth token)

# Write it back to .env
echo "GITHUB_CLASSIC_TOKEN=$TOKEN" > /root/.env
echo "GITHUB_FINEGRAINED_TOKEN=$TOKEN" >> /root/.env

# Verify
source /root/.env
curl -s -o /dev/null -w "%{http_code}" -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user
# Expected: 200
```

## Prevention

- Do not treat `.env` as the single source of truth for GitHub auth
- Always check `gh auth status` first when diagnosing GitHub auth issues
- If `gh` is authenticated but `.env` is stale, recover via `gh auth token` rather than asking the user for a new token
- Consider adding `gh auth token` to the startup detection routine in `scripts/gh-env.sh`

## Session Context

- **Date:** 2026-05-31
- **User:** leegordo
- **Repo:** leegordo/0xcreative
- **Agent:** Signal agent via Hermes messaging gateway
- **Fix applied:** Recovered token → rewrote `.env` → added SSH deploy key → force-pushed to GitHub Pages
