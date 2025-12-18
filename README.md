# Aethor Discord Bot

A Python Discord bot for Minecraft MMORPG server, Aethor.

## Features
- Slash and prefix commands (`/ping`, `!ping`)
- Admin utilities (sync commands, reload cogs)
- Minecraft server status via `mcstatus`
 - Roles management (grant/revoke roles)
 - Whitelist management (add/remove/list Minecraft names)
 - Optional RCON integration to apply changes to the server

## Quick Start (Windows)
1. Create venv:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate
   ```
2. Install deps:
   ```powershell
   pip install -r requirements.txt
   ```
3. Configure environment:
   - Copy `.env.example` to `.env`
   - Set `DISCORD_TOKEN`, optional `GUILD_ID`, `MC_SERVER`
4. Smoke-check (no token needed):
   ```powershell
   python src\bot.py --check
   ```
5. Run bot (requires `DISCORD_TOKEN`):
   ```powershell
   python src\bot.py --sync
   ```

## Environment Variables
- `DISCORD_TOKEN`: Discord bot token (required to run)
- `GUILD_ID`: Guild ID for faster slash sync (optional)
- `ADMIN_ROLE_IDS`: Comma-separated role IDs with admin powers (optional)
- `MC_SERVER`: Default server address, e.g. `play.example.com:25565`
 - Data files are stored under `data/` (e.g., `whitelist.json`).

## Notes
- Prefix commands use `!`. Slash commands are under the bot's app commands.
- Use `--sync` on first run to publish slash commands.
 - Economy features are scaffolded as comments in `src/cogs/economy.py` and not active.

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

## Diff Preview
- Commands:
   - `!wldiff` / `/whitelist_diff`
- Shows what would be added/removed compared to the server without applying changes.

## Commands
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
 - Status:
    - `!status` / `/status` — shows RCON state, next auto-sync time, local and server whitelist counts.
