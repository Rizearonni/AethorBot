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
