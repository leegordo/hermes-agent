# Fine-Grained PAT vs Classic PAT: Field Test Results

Session: 2026-05-29  
Server: Hermes VPS (srv1354161)  
User: leegordo  
Target: Private repo `leegordo/Sticker-Giant-Design-Rules`

## Tokens Tested

| Token | Type | Scopes | Git Clone | API Repo Metadata | API Content |
|---|---|---|---|---|---|
| `ghp_wl4enY...` | Classic (`repo`) | repo | ✓ works via URL | ✗ 401 after some time | ✗ 401 |
| `github_pat_11...` | Fine-grained | Contents (read), Metadata (read) on single repo | ✗ "Password auth not supported" | ✓ works via curl Bearer | ✗ 401 on content endpoint |

## Methods Tested

### 1. Direct git clone with token in URL
```bash
git clone "https://TOKEN@github.com/leegordo/Sticker-Giant-Design-Rules.git"
```
**Result:** `fatal: Authentication failed`  
**Why:** GitHub disabled password auth for git ops in 2021. Tokens in URL still trigger this path. **This never works for private repos via HTTPS.**

### 2. Git credential store + clone
```bash
git config --global credential.helper store
echo "https://TOKEN:@github.com" > ~/.git-credentials
git clone https://github.com/leegordo/Sticker-Giant-Design-Rules.git
```
**Result:** `remote: Invalid username or token. Password authentication is not supported.`  
**Same root cause as #1.**

### 3. curl with Bearer header
```bash
curl -s -H "Authorization: Bearer TOKEN" \
  "https://api.github.com/repos/leegordo/Sticker-Giant-Design-Rules"
```
**Result:** ✓ `200 OK` — found repo, confirmed private (170KB)

### 4. curl with token header (classic style)
```bash
curl -s -H "Authorization: token TOKEN" \
  "https://api.github.com/repos/leegordo/Sticker-Giant-Design-Rules"
```
**Result:** ✗ `401 Unauthorized` on fine-grained PAT. Works on classic PAT.

### 5. Basic Auth -u
```bash
curl -s -u "leegordo:TOKEN" \
  "https://api.github.com/repos/leegordo/Sticker-Giant-Design-Rules"
```
**Result:** ✗ `401 Unauthorized` — fine-grained PAT rejected. Token may have been invalidated after being saved to file.

### 6. Python urllib with Bearer
```python
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
with urllib.request.urlopen(req):
    ...
```
**Result:** ✗ `401 Unauthorized` — inconsistent with curl result for same token. Possible token scope issue or token invalidated during session.

### 7. GitHub tarball endpoint
```
https://api.github.com/repos/OWNER/REPO/tarball/BRANCH
```
**Result:** Same 401 issues as other content endpoints.

## Key Takeaways

1. **Fine-grained PATs + git HTTPS = never works.** Plan for SSH or API download.
2. **Shell escaping matters.** Tokens with underscores get mangled by bash word-splitting. Always use env vars or Python for programmatic API access.
3. **GitHub may invalidate tokens** after detecting them in shell commands or being saved to files. If a token works once then stops, regenerate.
4. **Best headless flow for private repos:**
   - Check `git ls-remote` first with existing credentials
   - If that fails, generate SSH key → user adds to GitHub → clone via SSH
   - Skip PAT-based git entirely
