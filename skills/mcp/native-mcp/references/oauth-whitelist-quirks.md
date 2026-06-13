# OAuth Whitelist Quirks for Remote MCP Servers

## Figma MCP Server

- **Official endpoint**: `https://mcp.figma.com/mcp` via Streamable HTTP
- **Auth method**: OAuth only. Figma maintains an allowlist of MCP clients.
- **Hermes CLI (headless VPS)**: `403 Forbidden` on OAuth registration. Hermes is NOT in Figma's client allowlist.
- **Claude Code**: ✓ Connected (Anthropic is in Figma's allowlist).
- **Cursor**: ✓ Connected (Cursor is in Figma's allowlist).
- **VS Code + GitHub Copilot**: ✓ Connected (Microsoft is in Figma's allowlist).
- **Workaround for Hermes**: Use community stdio server `@tmegit/figma-developer-mcp` with a Personal Access Token.

## Pattern: Service-Gated OAuth

Some SaaS MCP endpoints gate OAuth by client identity:
1. Server sends `403` during registration if `client_id` is unknown.
2. Browser-based clients (IDEs) are pre-registered.
3. Headless agents must either:
   - Be added to allowlist (contact vendor)
   - Use an alternative transport (stdio community server)
   - Proxy through a registered client (extract tokens from Claude/Cursor, fragile)

## Mitigation Heuristic

When `hermes mcp add` fails with OAuth errors on a known SaaS endpoint:
1. Check if `claude mcp list` shows it as connected.
2. If yes, the server is OAuth-gated by client identity — do NOT retry with Hermes.
3. Fall back to:
   - Community stdio server with PAT
   - `claude` CLI for that specific workflow
   - Local desktop server via Tailscale/SSH tunnel

## Token Confusion Pitfall

Figma has TWO tokens:
- **Personal Access Token (PAT)**: `figd_...`. Works with REST API and community stdio MCP servers. Set in `FIGMA_TOKEN` env var.
- **OAuth Bearer Token**: Issued during browser OAuth. Works with official `mcp.figma.com`. Cached by Claude Code, not extractable.

Do NOT try to use PAT as Bearer on `mcp.figma.com` — it will 401.
Do NOT try to use OAuth token on REST API — it may not have the right scopes.
