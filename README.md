# Aethor Discord Bot

A Python Discord bot for Minecraft MMORPG server, Aethor.

## Features
- Slash and prefix commands (`/ping`, `!ping`)
- Admin utilities (sync commands, reload cogs)
- Minecraft server status via `mcstatus`
 - Roles management (grant/revoke roles)
 - Whitelist management (add/remove/list Minecraft names)
 - Optional RCON integration to apply changes to the server
 - Onboarding: `/verify` links a Minecraft name, whitelists, and grants a role
 - Moderation: kick/ban/unban, timeout/untimeout, mute/unmute (role), purge, slowmode, lock/unlock, with logging

## Quick Start (Windows)
1. Install Poetry:
   https://python-poetry.org/docs/#installation
2. Install deps:
   ```powershell
   poetry install
   ```
3. Configure environment:
   - Copy `.env.example` to `.env`
   - Set `DISCORD_TOKEN`, optional `GUILD_ID`, `MC_SERVER`
4. Smoke-check (no token needed):
   ```powershell
   poetry run python -m src.bot --check
   ```
5. Run bot (requires `DISCORD_TOKEN`):
   ```powershell
   poetry run python -m src.bot --sync
   ```

## Environment Variables
- `DISCORD_TOKEN`: Discord bot token (required to run)
- `GUILD_ID`: Guild ID for faster slash sync (optional)
- `ADMIN_ROLE_IDS`: Comma-separated role IDs with admin powers (optional)
- `MC_SERVER`: Default server address, e.g. `play.example.com:25565`
 - Data files are stored under `data/` (e.g., `whitelist.json`).
 - Onboarding:
    - `VERIFIED_ROLE_ID`: Role to grant upon successful verification (optional)
    - `VERIFY_LOG_CHANNEL_ID`: Channel to log verifications (optional)
 - Moderation:
    - `MOD_LOG_CHANNEL_ID`: Channel to receive moderation action logs
    - `MUTE_ROLE_ID`: Role to use for `/mute` (optional)

## Notes
- Prefix commands use `!`. Slash commands are under the bot's app commands.
- Use `--sync` on first run to publish slash commands.
 - Economy features are scaffolded as comments in `src/cogs/economy.py` and not active.

## Operations
- Install dependencies and optional voice support:
   ```powershell
   poetry install
   ```
- Validate setup without logging in:
   ```powershell
   poetry run python -m src.bot --check
   ```
- First run and slash sync:
   ```powershell
   poetry run python -m src.bot --sync
   ```
- Windows service (optional): use NSSM to run the bot in the background
   ```powershell
   nssm install AethorBot "C:\\Path\\to\\poetry.exe" "run" "python" "-m" "src.bot" "--sync"
   nssm set AethorBot AppDirectory "D:\\AethorBot"
   nssm start AethorBot
   ```
- Logging: Bot logs to stdout; capture via your service manager or redirect PowerShell output.
- Known warnings: Voice support warning appears if `PyNaCl` is not installed; it's safe to ignore.
   The extension loading has been updated to async to avoid the "load_extension was never awaited" warning.

## Healthcheck
- Enable via env: `HEALTHCHECK_ENABLED=true`.
- Port selection:
   - If `HEALTHCHECK_PORT` is set, the server binds to that port.
   - On Pterodactyl/Revivenode, the panel sets `PORT`; we auto-fallback to it if provided.
- Endpoints: `GET /`, `/health`, `/healthz`, `/ready`, `/live` → returns JSON with `{ ok, uptime_seconds, guilds, latency_ms, ready }`.

## File Logging
- Enable via env: `FILE_LOGS_ENABLED=true`.
- Defaults: writes rotating logs to `logs/aethor.log` (1MB, 5 backups).
- Customize with:
   - `FILE_LOGS_PATH`, `FILE_LOGS_MAX_BYTES`, `FILE_LOGS_BACKUP_COUNT`.

## Revivenode Deployment
- Create a Discord Bot service (Python) in the Revivenode panel (Pterodactyl).
- Upload files via SFTP: `src/`, `data/`, `requirements.txt`, `.env.example`, `README.md`.
   - Data persistence: everything under `/home/container` persists; the bot uses `data/` for state.
- Environment config (Panel → Variables or Startup): set at minimum `DISCORD_TOKEN`; optionally set `GUILD_ID`, `MC_SERVER`, `RCON_*`, `LOG_CHANNEL_ID`, `VERIFIED_ROLE_ID`, `VERIFY_LOG_CHANNEL_ID`, `MOD_LOG_CHANNEL_ID`, `MUTE_ROLE_ID`.
   - Optional ops vars: `HEALTHCHECK_ENABLED`, `HEALTHCHECK_PORT` (panel may set `PORT`), `FILE_LOGS_ENABLED`, `FILE_LOGS_PATH`, `FILE_LOGS_MAX_BYTES`, `FILE_LOGS_BACKUP_COUNT`.
- Startup command (Startup tab):
   - `python -m src.bot --sync`
   - After the first sync, you can use `python -m src.bot`.
- Install dependencies (if the egg supports Auto-Install): click Install. Otherwise run in Console:
   ```bash
   poetry install
   ```
- First run: Start the server. Watch the console for "Synced" and "Logged in as".
   - Health: The panel may expose the assigned port for checks; the health endpoint returns 200 JSON when the bot is up.
- RCON tips:
   - Ensure your Minecraft server `server.properties` has RCON enabled and the port open to the bot host.
   - Use the server's public IP for `RCON_HOST` and the RCON port/password from your config.
- Updates:
   - Upload changed files via SFTP, then restart. Use `/sync` to update slash commands when needed.

## RCON Integration
- Enable RCON in your `server.properties`:
   - `enable-rcon=true`
   - `rcon.port=25575` (default)
   - `rcon.password=your_password`
- Configure `.env`:
   - `RCON_ENABLED=true`
   - `RCON_HOST=127.0.0.1` (or your server IP)
   - `RCON_PORT=25575`
   - `RCON_PASSWORD=your_password`
- Behavior:
   - When `RCON_ENABLED=true`, `whitelist_add`/`whitelist_remove` will also issue server commands via RCON.
   - Use `/whitelist_list_server` to read the current server whitelist via RCON.
   - Local list is stored in `data/whitelist.json`; treat it as your source of truth for bot features.

## Auto Sync (Nightly)
- Configure `.env`:
   - `AUTO_SYNC_ENABLED=true`
   - `AUTO_SYNC_HOUR=3` (24h format)
   - `AUTO_SYNC_MINUTE=0`
   - `AUTO_SYNC_REMOVE_EXTRAS=false` (set `true` to remove server-only names)
   - `LOG_CHANNEL_ID=<channel_id>` (optional: posts nightly summary there)
- Behavior:
   - Runs daily at the configured time and applies local list to server.
   - Respects `AUTO_SYNC_REMOVE_EXTRAS` for removal.
   - Posts summary to `LOG_CHANNEL_ID` when set; reports skipped/error states.

## Backups
- Environment:
   - `BACKUP_ENABLED=true` — enable timestamped backups of `whitelist.json`.
   - `BACKUP_MAX_KEEP=10` — retain last N backups in `data/backups/`.
- When Backups Run:
   - After `/whitelist_import` completes.
   - After manual `/whitelist_sync` and `!wlsync` complete.
   - After nightly auto-sync completes.

## Diff Preview
- Commands:
   - `!wldiff` / `/whitelist_diff`
- Shows what would be added/removed compared to the server without applying changes.

## Commands
 - Moderation:
    - `/kick member:<@User> reason:<text?>`
    - `/ban member:<@User> delete_message_days:<int=0> reason:<text?>`
    - `/unban user_id:<id> reason:<text?>`
    - `/timeout member:<@User> minutes:<int> reason:<text?>`
    - `/untimeout member:<@User> reason:<text?>`
    - `/mute member:<@User> reason:<text?>` / `/unmute member:<@User> reason:<text?>`
    - `!purge <count>` / `/purge count:<int>`
    - `/slowmode seconds:<int> channel:<#channel?>`
    - `/lock channel:<#channel?>` / `/unlock channel:<#channel?>`
- Roles:
   - `!rolegrant @Role @User` / `/role_grant role:<Role> member:<User?>`
   - `!rolerevoke @Role @User` / `/role_revoke role:<Role> member:<User?>`
- Whitelist:
   - `!wladd <name>` / `/whitelist_add name:<str>`
   - `!wlremove <name>` / `/whitelist_remove name:<str>`
   - `!wllist` / `/whitelist_list`
   - `!wlsync [remove_extras]` / `/whitelist_sync remove_extras:<bool>`
   - When `LOG_CHANNEL_ID` is set, manual sync posts a summary to that channel.
   - Manual sync cooldown per user: `SYNC_COOLDOWN_SECONDS` (default 30s)
   - `/whitelist_import file:<attachment> apply_rcon:<bool>` — upload a CSV or TXT of IGNs (one per line or comma/CSV). Adds to local whitelist; when `apply_rcon=true` and RCON is enabled, also runs `whitelist add` for each name.
   - `/whitelist_export as_csv:<bool>` — download the current whitelist as JSON (default) or newline CSV.
 - Onboarding:
    - `/verify name:<str>` — links your Minecraft IGN (resolves UUID), adds to whitelist (and RCON if enabled), and grants `VERIFIED_ROLE_ID` if configured.
    - `/whois user:<@User?>` — shows a user's linked IGN/UUID.
    - `/unverify` — self-remove verification, role, and whitelist entry; uses RCON if enabled.
    - `/unverify_user user:<@User>` — admin-only: unverify another user, remove role and whitelist; uses RCON if enabled.
    - Safety: unverify commands refuse to run if the player appears online (checked via RCON `list`, or mcstatus query/status as fallback).
 - Status:
    - `!status` / `/status` — shows RCON state, next auto-sync time, local and server whitelist counts.
