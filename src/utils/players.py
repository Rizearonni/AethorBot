import json
import os
from typing import Any

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "data")
PLAYERS_PATH = os.path.normpath(os.path.join(DATA_DIR, "players.json"))


def ensure_files() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(PLAYERS_PATH):
        with open(PLAYERS_PATH, "w", encoding="utf-8") as f:
            json.dump({}, f)


def read_players() -> dict[str, Any]:
    ensure_files()
    with open(PLAYERS_PATH, encoding="utf-8") as f:
        try:
            data = json.load(f)
        except Exception:
            data = {}
    if not isinstance(data, dict):
        return {}
    return data


def write_players(data: dict[str, Any]) -> None:
    ensure_files()
    with open(PLAYERS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def set_player(discord_id: int, name: str, uuid: str | None) -> None:
    data = read_players()
    data[str(discord_id)] = {
        "name": name,
        "uuid": uuid or "",
    }
    write_players(data)


def get_player(discord_id: int) -> dict[str, Any] | None:
    data = read_players()
    return data.get(str(discord_id))


def delete_player(discord_id: int) -> bool:
    data = read_players()
    key = str(discord_id)
    if key in data:
        data.pop(key)
        write_players(data)
        return True
    return False
