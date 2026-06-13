# Parallel Subagent Directory Contract

## Problem

When multiple subagents work on the same project simultaneously, they can:
- Overwrite each other's files
- Create conflicting directory structures
- Duplicate shared assets (CSS, JS) with subtle differences
- Leave the orchestrator with a merge nightmare

## Solution: Directory Contract

Define the filesystem contract BEFORE spawning subagents. The orchestrator creates the skeleton; subagents fill their assigned slots.

### Example: Multi-Section Static Site

```
~/Projects/0xcreative/           # Orchestrator creates this
├── index.html                   # Orchestrator builds (landing)
├── assets/
│   ├── css/
│   │   └── 0xcreative.css      # Orchestrator creates shared design system
│   ├── js/                      # Orchestrator creates shared scripts
│   └── images/                  # Orchestrator creates, subagents populate
├── committee/                   # Subagent 1 owns this
│   ├── index.html
│   └── ideas/
│       └── idea-001/
│           ├── index.html
│           ├── meta.json
│           └── demo/
│               └── index.html
├── blog/                        # Subagent 2 owns this
│   ├── index.html
│   └── posts/
├── gallery/                     # Orchestrator or Subagent 3
├── factory/
└── portal/
```

### Contract Rules

1. **Orchestrator owns the root** — creates shared assets, landing page, navigation
2. **Each subagent gets one top-level directory** — they have write access only there
3. **Shared assets are read-only** — subagents reference `../assets/css/...` but never modify
4. **No cross-directory writes** — subagent working on `blog/` never touches `committee/`
5. **Consistent naming** — all section index files named `index.html` for clean URLs

### Pre-Spawn Checklist

- [ ] Create shared CSS/JS/assets before spawning any subagent
- [ ] Document the relative path from each subagent's directory to shared assets
- [ ] Give each subagent its exact output path in the context
- [ ] Tell subagents explicitly: "Do NOT create your own CSS. Use the shared design system at `../../assets/css/...`"

### Post-Spawn Merge

After all subagents return:
1. Verify each assigned directory has the expected files
2. Check that all pages link to shared assets with correct relative paths
3. Test navigation between sections (relative links like `../blog/`)
4. Run a local preview server to verify the full site

## Variations

**For GitHub Pages:** All paths must be relative (no root-absolute `/css/...` links) because the site may be served from a subdirectory like `username.github.io/repo-name/`.

**For parallel code tasks:** Same pattern applies — shared `lib/` or `utils/` directory, each subagent owns a feature module.
