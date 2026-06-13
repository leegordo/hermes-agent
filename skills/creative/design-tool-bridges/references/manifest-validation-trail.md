# Manifest Validation Trail — DoodleHaus Bridge

Session: DoodleHaus → Figma plugin push project. User hit four sequential manifest errors and fixed them live.

## Initial manifest (broken)

```json
{
  "editorType": ["figma"],
  "networkAccess": {
    "allowedDomains": ["*"],
    "devAllowedDomains": ["localhost:*", "127.0.0.1:*", "leegordo.github.io"]
  }
}
```

## Error chain

### Error 1: Missing `networkAccess.reasoning`
> "Manifest error: Invalid value for networkAccess. If you want to allow all domains, please add a `reasoning` field to the networkAccess object."

**Fix**: Added `networkAccess.reasoning` string.

### Error 2: Invalid URL format in `devAllowedDomains`
> "Manifest error: Invalid value for devAllowedDomains. `localhost:*` must be a valid URL."

**Fix**: `localhost:*` → `http://localhost`. Same for `127.0.0.1:*` → `http://127.0.0.1`. Added `https://` prefix to `leegordo.github.io`.

### Error 3: IP addresses rejected
> "Manifest error: Invalid value for devAllowedDomains. `http://127.0.0.1` must be a valid URL."

**Fix**: Removed `http://127.0.0.1` entirely. Figma does not accept IP addresses even with protocol. `http://localhost` covers localhost.

### Error 4: Missing `"dev"` in `editorType`
> "Manifest error: The manifest editorType does not include `dev`."

**Fix**: Added `"dev"` to `editorType`: `["figma", "dev"]`.

## Final valid manifest

```json
{
  "editorType": ["figma", "dev"],
  "networkAccess": {
    "allowedDomains": ["*"],
    "devAllowedDomains": ["http://localhost", "https://leegordo.github.io"],
    "reasoning": "The plugin fetches DoodleHaus design JSON from external URLs and loads image assets referenced in generated designs."
  }
}
```
