---
name: static-site-deployment
description: "Deploy static HTML/CSS/JS sites to Netlify with GitHub source control. Full workflow from build to live URL."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [Netlify, GitHub, Static Sites, Deployment, CLI, Prototyping]
    related_skills: [github-repo-management, remote-static-preview, portfolio-website-redesign]
---

# Static Site Deployment

Deploy static HTML/CSS/JS sites to Netlify with GitHub as the source-of-truth. This is the standard workflow for creative prototypes, landing pages, concept demos, and portfolio pieces.

## When to Use

- User asks for a "landing page", "demo", "prototype", or "concept"
- User says "deploy this" or "host this somewhere"
- User wants "a place to deploy concepts"
- Any static HTML/CSS/JS output that needs a live URL

**Default target:** For this user, GitHub Pages (leegordo.github.io/<repo>) is the default for creative work and portfolio pieces. Netlify is fallback only if the Netlify CLI + token are already working. VPS static preview is last resort.

## Decision Tree

```
Is gh CLI authenticated?
├── YES → Use GitHub Pages (fastest, no extra tokens)
│         └── Build → git init → commit → gh repo create --public --source=. --push
│             → API call to enable Pages → live at leegordo.github.io/<repo>
└── NO  → Can we authenticate gh quickly?
          ├── YES → GitHub Pages
          └── NO  → Try Netlify (if CLI installed + token has site scope)
                    └── Failing that → VPS raw serve (emergency only)
```

## File Structure Convention

For predictable deployment, use this structure:

```
my-project/
├── index.html          # Entry point (required)
├── style.css           # Or inline styles
├── script.js           # Or inline scripts
└── assets/             # Images, fonts, etc.
```

Single-file HTML (`index.html` with inline CSS/JS) is preferred for prototypes — zero build step, one file to track.

## Prerequisites

- `git` configured with identity (see `github-auth` skill)
- `gh` CLI authenticated (see `github-auth` skill)
- For Netlify: Node.js/npm available (for Netlify CLI install)

---

## Target A: GitHub Pages (Default)

GitHub Pages is free, fast, and keeps everything in one place (GitHub). Best for portfolios, concept demos, and static creative work.

### Step 1: Build the Site

Create the static files in a dedicated directory under `~/Projects/`:

```bash
mkdir -p ~/Projects/<project-name>
# Write index.html, assets, etc.
```

For single-page creative landers, a single `index.html` with embedded CSS/JS is often enough. For multi-page sites, use a directory structure with `index.html` at the root.

### Step 2: Initialize Git and Push to GitHub

```bash
cd ~/Projects/<project-name>
git init
git add .
git commit -m "feat: initial site"
git branch -m main

# Create public repo and push
gh repo create <repo-name> --public --source=. --push
```

**Naming:** Use short descriptive names. The live URL will be `https://leegordo.github.io/<repo-name>/`.

### Step 3: Enable GitHub Pages

```bash
# Enable Pages on the main branch, root directory
gh api repos/leegordo/<repo-name>/pages \
  -X POST \
  -f source='{"branch":"main","path":"/"}' 2>/dev/null || \
gh api repos/leegordo/<repo-name>/pages \
  -H "Accept: application/vnd.github+json" \
  -X PUT \
  -f source='{"branch":"main","path":"/"}'
```

Or enable manually: **https://github.com/leegordo/<repo-name>/settings/pages** → Source: Deploy from a branch → `main` / `/(root)`.

### Step 4: Verify the Live URL

```bash
# Check Pages status
gh api repos/leegordo/<repo-name>/pages --jq '.html_url, .status'
```

Live URL will be: `https://leegordo.github.io/<repo-name>/`

Allow 30-60 seconds for the first build. If the repo existed before with different content, force-push or clear the Pages cache by making a new commit.

### Step 5: Subsequent Deploys

After initial setup, redeploying is just:

```bash
cd ~/Projects/<project-name>
git add . && git commit -m "update: ..." && git push
```

GitHub Pages rebuilds automatically on push.

---

## Target B: Netlify (Fallback)

Use Netlify when you need branch deploys, form handling, edge functions, or when GitHub Pages constraints (no server-side logic, 1GB soft limit) are too restrictive.

### Step 1: Build the Site

Same as GitHub Pages Step 1 above.

### Step 2: Initialize Git and Push to GitHub

Same as GitHub Pages Step 2 above. Netlify can deploy from a GitHub repo.

### Step 3: Install Netlify CLI

```bash
# Check if already installed
netlify --version

# Install if missing — USE FOREGROUND with long timeout
# Background install with notify_on_complete fails silently for this package
npm install -g netlify-cli
```

**Pitfall:** Do NOT use `terminal(background=true, notify_on_complete=true)` for Netlify CLI install. The background process produces no output and times out. Use foreground with `timeout=300`.

### Step 4: Authenticate Netlify

On headless servers, the browser login flow (`netlify login`) does not work. Use a Personal Access Token (PAT):

```bash
# User provides their Netlify PAT (nfp_...)
export NETLIFY_AUTH_TOKEN="<pat-here>"
netlify status
```

**Security:** Do NOT write the PAT into commands for the user to run. The user's security tooling blocks credential-containing terminal commands. Instead, tell the user:

> Run this with your PAT:
> ```
> export NETLIFY_AUTH_TOKEN="your_pat_here"
> netlify status
> ```

### Step 5: Link and Deploy

```bash
cd ~/Projects/<project-name>

# Link to a Netlify site (creates new or links existing)
netlify link

# Deploy to production
netlify deploy --prod --dir=.
```

For first deploys, `netlify link` will ask to create a new site. Accept the defaults. The deploy command outputs the live URL.

### Step 6: Subsequent Deploys

After the initial setup, redeploying is just:

```bash
cd ~/Projects/<project-name>
git add . && git commit -m "update: ..." && git push
netlify deploy --prod --dir=.
```

---

## Target C: VPS Raw Serve (Emergency Only)

If neither GitHub Pages nor Netlify works, serve locally on the VPS and expose via the public IP. Users with an established GitHub Pages workflow find VPS IP previews frustrating — always prefer pushing to the repo they already own.

**When to use VPS preview:**
- GitHub auth is completely broken AND cannot be fixed in-session
- User explicitly asks for a temporary preview before committing
- Firewall/network issues block all other methods

**When NOT to use VPS preview:**
- User mentions an existing GitHub Pages site
- Repo already exists and just needs updated content
- `gh` CLI is authenticated and working

### The Complete VPS Checklist

#### 1. Bind to `0.0.0.0`, not `127.0.0.1`

```bash
# WRONG — localhost only, unreachable externally
python3 -m http.server 8000

# RIGHT — listen on all interfaces
python3 -m http.server 8000 --bind 0.0.0.0
```

When using `terminal(background=true)`, the command should be:
```bash
python3 -m http.server 8000 --bind 0.0.0.0
```
Do NOT wrap with `nohup` or shell backgrounding — Hermes manages lifecycle better via `process()`.

#### 2. Open the Firewall

```bash
ufw allow 8000/tcp && ufw allow 8001/tcp && ufw allow 8002/tcp
```

**Pitfall:** Most VPS providers ship with `ufw` active on 22/80/443 only. Non-standard ports (8000+) are blocked by default. *Always verify after opening*:
```bash
ss -tlnp | grep 8000
```

#### 3. Get the Public IP

```bash
curl -s icanhazip.com
```

**Pitfall:** IPv6-only ISPs or CGNAT IPv4 may make `icanhazip.com` return nothing useful. If the user is on Tailscale, prefer the Tailnet IP (e.g., `100.x.x.x`) since it's always reachable regardless of upstream network shape.

#### 4. Verify End-to-End

From the VPS itself, confirm the server responds on its *own* public IP:
```bash
curl -s -o /dev/null -w "%{http_code}" http://<PUBLIC_IP>:8000/
```

If this returns `200`, the serve + firewall combo is working. If `Connection refused`, the server isn't bound or the port is firewalled. If `403`, check directory permissions.

#### 5. Give the User the Right URL

```
Your preview is live at:
http://<PUBLIC_IP>:8000/
```

If the user is on Tailscale, use the Tailnet IP — it's private and encrypted:
```
Tailscale: http://100.84.76.9:8000/
```

### Tailscale Serve (Preferred When Available)

If the user has Tailscale running (`tailscale status` shows connected), use `tailscale serve` instead of raw ports:

```bash
# Serve a directory
nohup tailscale serve --bg --set-path=/preview1 /tmp/portfolio-v1-editorial &
```

Benefits:
- HTTPS automatically via Let's Encrypt
- No firewall rules needed (tailnet is encrypted overlay)
- Stable hostname: `https://<machine-name>.<tailnet-name>.ts.net/preview1`
- Works through CGNAT and restrictive ISPs

Verify:
```bash
tailscale serve status
```

### Netlify Drag-and-Drop (When Ports Are Blocked)

If the user's network blocks non-standard HTTP ports, or you need a permanent shareable URL without CLI setup:

1. Zip the directory: `zip -r preview.zip /tmp/preview-dir/`
2. Go to `https://app.netlify.com/drop`
3. Upload the zip
4. Get instant URL

**Pitfall:** Netlify drag-and-drop deploys have 48-hour expiry unless linked to a site. For permanent previews, use `netlify deploy --prod` or connect to a Git repo.

---

## Multi-Preview Workflow (Parallel Design Directions)

When the user requests multiple visual directions (e.g., 3 design concepts), use sequential ports with clear labeling:

```bash
# Direction 1 — Editorial
python3 -m http.server 8001 --bind 0.0.0.0  # in /tmp/dir1

# Direction 2 — Technical
python3 -m http.server 8002 --bind 0.0.0.0  # in /tmp/dir2

# Direction 3 — Bold
python3 -m http.server 8003 --bind 0.0.0.0  # in /tmp/dir3
```

Then open each port and present all three URLs together.

**Cleanup before restart:** If re-deploying to the same ports, kill old processes first:
```bash
pkill -f "http.server"
# or more precisely:
kill $(ss -tlnp | grep ':800[123]' | awk '{print $7}' | cut -d',' -f2 | cut -d'=' -f2)
```

**Pitfall:** When serving multiple directories in parallel, don't use `nohup &` — use `terminal(background=true)` for each, then capture session IDs. Verify all three are listening with `ss -tlnp`.

## Verification Checklist

- [ ] GitHub repo exists and `main` branch is pushed
- [ ] `netlify status` shows authenticated
- [ ] `netlify deploy --prod` outputs a live URL
- [ ] URL loads in browser without 404

## Maintenance: Restructuring an Active Multi-Page Site

When you remove or rename sections on a multi-page static site, stale links and nav items **will** remain in the HTML files you didn't touch. Verify on disk, not just the pages you edited.

### Pre-Deploy Audit (run on disk before every push)

```bash
# Find ALL HTML files recursively
cd ~/Projects/<repo>

# 1. Check for stale section names in links
find . -name "*.html" -exec grep -l "removed-section-name" {} \;

# 2. Verify nav consistency: every page should have identical nav items
find . -name "*.html" -print0 | while IFS= read -r -d '' f; do
  echo "=== $f ==="
  grep -c "<nav" "$f"
done

# 3. Check for root-relative links that break on project-site hosting
grep -rn 'href="/' --include="*.html" .

# 4. Check for inconsistent footer text
grep -rn "footer text" --include="*.html" . | sort
```

If the user is refactoring a site and says "that's a leak from another project" or "this old nav is still showing," immediately run the audit commands above before any further changes.

### Bulk Fix Patterns

**Remove all references to a deleted section:**
```bash
# Remove lines that link to the old section
find . -name "*.html" -exec sed -i '/href=".*old-section"/d' {} \;
```

**Update footers across all pages:**
```bash
find . -name "*.html" -exec sed -i 's|Old Footer Text|New Footer Text|g' {} \;
```

**Fix relative path depths after moving directories:**
```bash
# In files two levels deep (e.g., blog/posts/), replace ../ with ../../
find ./blog/posts -name "*.html" -exec sed -i 's|"../assets/|"../../assets/|g' {} \;
```

### When to Use a Subagent for Quality Audit

For sites with 5+ pages, delegate a subagent with this toolset: `browser`, `web`, `file`, `terminal` and a detailed checklist covering:
1. Visit every reachable page via browser navigation
2. Test every internal link
3. Check console for 404 assets
4. Verify nav consistency (same items, correct relative paths)
5. Verify footer consistency
6. Verify CSS loads on every page
7. Check for stale references to removed sections

## Post-Deploy Quality Audit Checklist

Run this checklist after deploying — and after any refactor that touches nav, structure, shared components, CSS, or base paths.

### When to audit
- Nav structure changed (items added/removed/reordered)
- Footer text or layout changed
- Shared CSS file modified
- New subdirectory of pages added (blog posts, gallery systems, etc.)
- Domain or base path changed (e.g. root site → GitHub Pages project site)
- User reports "something looks broken on mobile"

### Viewport meta tag ( Critical for mobile )

Every page MUST have:
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

```bash
# Find files missing the viewport tag
grep -L "viewport" --include="*.html" -r .
# -L = files that DON'T match
```

### Asset loading depth check ( Critical )

```bash
# Check CSS links are correct for each directory level
grep -r "style.css" --include="*.html" .
# Root pages:    ./style.css
# One level deep: ../style.css
# Two levels deep: ../../style.css
```

### Mobile responsive pass ( Medium )

Test at 375px (iPhone SE) and 768px (iPad). If you don't have browser access, verify the CSS contains a comprehensive `@media` block:

```css
@media (max-width: 768px) {
  nav { padding: 12px 16px; flex-wrap: wrap; }
  .container { padding: 0 1rem; }
  .page-content { padding-top: 80px; }
  .hero { padding: 6rem 1rem 3rem; min-height: auto; }
  .hero-cta { flex-direction: column; width: 100%; }
  .hero-cta .btn { width: 100%; justify-content: center; }
  .card-grid { grid-template-columns: 1fr; gap: 1rem; }
  h1 { font-size: clamp(2rem, 8vw, 3rem); }
  h2 { font-size: clamp(1.25rem, 5vw, 1.75rem); }
  .section-header { flex-direction: column; align-items: flex-start; }
  pre { padding: 0.75rem; font-size: 0.8rem; }
}
```

**Checklist:**
- [ ] No horizontal overflow (`overflow-x: scroll` on body)
- [ ] Nav fits or wraps gracefully (no overlapping items)
- [ ] Hero text scales with `clamp()` — not fixed large sizes
- [ ] CTAs stack vertically, full-width
- [ ] Cards go single-column
- [ ] Grid layouts collapse gracefully
- [ ] Touch targets ≥ 44px tall
- [ ] Font sizes ≥ 14px for body text
- [ ] Padding comfortable but not excessive (16px sides, not 40px)
- [ ] Code blocks don't overflow viewport

### Content freshness ( Low )
- No "Coming Soon" on shipped features
- No placeholder text (Lorem ipsum, "TODO", etc.)
- Dates and version numbers are current

### Quick verification commands
```bash
# After fixes, verify nothing stale remains across all pages
grep -rl "OLD_TEXT" --include="*.html" . || echo "Clean"

# Count HTML files (sanity check on coverage)
find . -name "*.html" | wc -l
```

### Common pitfalls
- **Sub-pages are invisible until you look.** Blog posts, gallery systems, idea briefs — these are the first to break during refactors because they're not in the main nav file.
- **@media blocks are often too minimal.** A 5-line mobile breakpoint is almost always insufficient. Plan for 50+ lines covering nav, hero, grids, cards, buttons, and typography.
- **Viewport meta tag is easy to forget on new pages.** Use `grep -L` to find pages missing it.
- **Footer text is copy-pasted, not included.** When you change the footer in one place, grep for the old text across all HTML files.

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Pages returns 404 | Build hasn't finished | Wait 30-60s, retry |
| **Logo/home link goes to wrong domain root** | `href="/"` resolves to `github.io/` instead of `github.io/repo/` | Use `href="./"` or `href="index.html"` for project sites. Verify with `grep -rl 'href="/"' --include="*.html" .` before every deploy |
| Relative paths break on subpages | Deep pages use wrong `../` depth | Audit all `<a>`, `<link>`, `<img>`, `<script>` src/href values with subagent or `grep` on disk, not just browser check |
| Pages returns 404 persistently | Repo is private | GitHub Pages requires public repo for free tier. **Workaround:** Use a separate public repo for Pages while keeping source code in the private repo. |
| `gh repo create` fails | Not authenticated | Run `gh auth status`, re-auth if needed |
| Netlify "Unauthorized" | Token scope too narrow | Pivot to GitHub Pages |
| Netlify "No teams available" | Token not associated with team | Pivot to GitHub Pages |
| CSS/JS not loading | Relative path issues | Use `./style.css` not `/style.css` for subpath hosting |
| `npm install -g netlify-cli` hangs | Background install fails silently | Use foreground with `timeout=300`. Do NOT use `terminal(background=true)` for CLI install. |
| `netlify login` fails on server | No browser available | Use `NETLIFY_AUTH_TOKEN` env var instead |
| `netlify status` says "Not logged in" | Token not exported or invalid | Re-export `NETLIFY_AUTH_TOKEN` |
| Deploy succeeds but site 404s | `--dir` points to wrong directory | Ensure `--dir` contains `index.html` |
| `curl: (7) Failed to connect` from external host | Binding to `127.0.0.1` | Use `--bind 0.0.0.0` |
| `curl: (7) Failed to connect` from VPS itself | Server not running | Check `ps aux \| grep http.server` |
| `curl` times out externally but works locally | Firewall blocking port | `ufw allow <port>/tcp` |
| 403 Forbidden from VPS serve | Directory has no index.html | Check `ls` in serve directory |
| Port already in use | Another process claimed it | `ss -tlnp \| grep <port>` |
| "not loading" from user's browser | ISP blocks port 8000+ | Switch to Netlify or Tailscale serve |

## Related

- `github-auth` — GitHub authentication setup
- `github-repo-management` — Repo creation, remotes, releases
- `remote-static-preview` — Serve static files from the VPS directly (alternative to Netlify)
