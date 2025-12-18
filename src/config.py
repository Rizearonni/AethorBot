import os
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN: Optional[str] = os.getenv("DISCORD_TOKEN")
GUILD_ID: Optional[int] = None
try:
    gid = os.getenv("GUILD_ID", "0").strip()
    GUILD_ID = int(gid) or None
except ValueError:
    GUILD_ID = None

ADMIN_ROLE_IDS: List[int] = [
    int(x) for x in os.getenv("ADMIN_ROLE_IDS", "").split(",") if x.strip().isdigit()
]

MC_SERVER: str = os.getenv("MC_SERVER", "")


def require_token() -> None:
    if not DISCORD_TOKEN:
        raise RuntimeError("DISCORD_TOKEN is not set. Put it in .env or environment.")

# RCON configuration
def _get_bool(value: Optional[str]) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}

RCON_ENABLED: bool = _get_bool(os.getenv("RCON_ENABLED", "false"))
RCON_HOST: str = os.getenv("RCON_HOST", "127.0.0.1")
try:
    RCON_PORT: int = int(os.getenv("RCON_PORT", "25575"))
except ValueError:
    RCON_PORT = 25575
RCON_PASSWORD: str = os.getenv("RCON_PASSWORD", "")

# Auto sync configuration
AUTO_SYNC_ENABLED: bool = _get_bool(os.getenv("AUTO_SYNC_ENABLED", "false"))
try:
    AUTO_SYNC_HOUR: int = int(os.getenv("AUTO_SYNC_HOUR", "3"))
except ValueError:
    AUTO_SYNC_HOUR = 3
try:
    AUTO_SYNC_MINUTE: int = int(os.getenv("AUTO_SYNC_MINUTE", "0"))
except ValueError:
    AUTO_SYNC_MINUTE = 0
AUTO_SYNC_REMOVE_EXTRAS: bool = _get_bool(os.getenv("AUTO_SYNC_REMOVE_EXTRAS", "false"))

# Log channel
LOG_CHANNEL_ID: Optional[int] = None
try:
    lcid = os.getenv("LOG_CHANNEL_ID", "").strip()
    LOG_CHANNEL_ID = int(lcid) if lcid else None
except ValueError:
    LOG_CHANNEL_ID = None

# Manual sync cooldown
try:
    SYNC_COOLDOWN_SECONDS: int = int(os.getenv("SYNC_COOLDOWN_SECONDS", "30"))
except ValueError:
    SYNC_COOLDOWN_SECONDS = 30

# Onboarding / verification
VERIFIED_ROLE_ID: Optional[int] = None
try:
    vrole = os.getenv("VERIFIED_ROLE_ID", "").strip()
    VERIFIED_ROLE_ID = int(vrole) if vrole else None
except ValueError:
    VERIFIED_ROLE_ID = None

VERIFY_LOG_CHANNEL_ID: Optional[int] = None
try:
    vlc = os.getenv("VERIFY_LOG_CHANNEL_ID", "").strip()
    VERIFY_LOG_CHANNEL_ID = int(vlc) if vlc else None
except ValueError:
    VERIFY_LOG_CHANNEL_ID = None

# Backups
BACKUP_ENABLED: bool = _get_bool(os.getenv("BACKUP_ENABLED", "true"))
try:
    BACKUP_MAX_KEEP: int = int(os.getenv("BACKUP_MAX_KEEP", "10"))
except ValueError:
    BACKUP_MAX_KEEP = 10

# Moderation
MOD_LOG_CHANNEL_ID: Optional[int] = None
try:
    mlc = os.getenv("MOD_LOG_CHANNEL_ID", "").strip()
    MOD_LOG_CHANNEL_ID = int(mlc) if mlc else None
except ValueError:
    MOD_LOG_CHANNEL_ID = None

MUTE_ROLE_ID: Optional[int] = None
try:
    mrole = os.getenv("MUTE_ROLE_ID", "").strip()
    MUTE_ROLE_ID = int(mrole) if mrole else None
except ValueError:
    MUTE_ROLE_ID = None

# Healthcheck
HEALTHCHECK_ENABLED: bool = _get_bool(os.getenv("HEALTHCHECK_ENABLED", "false"))
_panel_port = os.getenv("PORT", "")  # Pterodactyl panels often expose PORT
try:
    HEALTHCHECK_PORT: int = int(os.getenv("HEALTHCHECK_PORT", _panel_port or "8080"))
except ValueError:
    HEALTHCHECK_PORT = 8080

# File logging
FILE_LOGS_ENABLED: bool = _get_bool(os.getenv("FILE_LOGS_ENABLED", "true"))
FILE_LOGS_PATH: str = os.getenv("FILE_LOGS_PATH", os.path.join("logs", "aethor.log"))
try:
    FILE_LOGS_MAX_BYTES: int = int(os.getenv("FILE_LOGS_MAX_BYTES", "1048576"))  # 1MB
except ValueError:
    FILE_LOGS_MAX_BYTES = 1048576
try:
    FILE_LOGS_BACKUP_COUNT: int = int(os.getenv("FILE_LOGS_BACKUP_COUNT", "5"))
except ValueError:
    FILE_LOGS_BACKUP_COUNT = 5
