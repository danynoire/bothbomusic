# bot_state.py
# Estado em memória por guild (sincronizado com dashboard)

from typing import Dict, Any

guild_states: Dict[int, Dict[str, Any]] = {}


def get_state(guild_id: int) -> Dict[str, Any]:
    if guild_id not in guild_states:
        guild_states[guild_id] = {
            "playing": False,
            "paused": False,
            "volume": 100,
            "loop": False,
            "queue": [],
            "current": None
        }
    return guild_states[guild_id]


def set_playing(guild_id: int, playing: bool) -> None:
    get_state(guild_id)["playing"] = bool(playing)


def set_paused(guild_id: int, paused: bool) -> None:
    get_state(guild_id)["paused"] = bool(paused)


def set_volume(guild_id: int, volume: int) -> None:
    volume = max(0, min(150, int(volume)))
    get_state(guild_id)["volume"] = volume


def toggle_loop(guild_id: int) -> bool:
    state = get_state(guild_id)
    state["loop"] = not state["loop"]
    return state["loop"]


def add_to_queue(guild_id: int, track) -> None:
    if track:
        get_state(guild_id)["queue"].append(track)


def pop_queue(guild_id: int):
    queue = get_state(guild_id)["queue"]
    if not queue:
        return None
    return queue.pop(0)


def clear_queue(guild_id: int) -> None:
    get_state(guild_id)["queue"].clear()


def set_current(guild_id: int, track) -> None:
    get_state(guild_id)["current"] = track
