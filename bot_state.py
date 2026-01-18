# bot_state.py

guild_states = {}

def get_state(guild_id: int) -> dict:
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


def set_playing(guild_id: int, playing: bool):
    get_state(guild_id)["playing"] = playing


def set_paused(guild_id: int, paused: bool):
    get_state(guild_id)["paused"] = paused


def set_volume(guild_id: int, volume: int):
    get_state(guild_id)["volume"] = volume


def toggle_loop(guild_id: int) -> bool:
    state = get_state(guild_id)
    state["loop"] = not state["loop"]
    return state["loop"]


def add_to_queue(guild_id: int, track):
    get_state(guild_id)["queue"].append(track)


def pop_queue(guild_id: int):
    queue = get_state(guild_id)["queue"]
    return queue.pop(0) if queue else None


def clear_queue(guild_id: int):
    get_state(guild_id)["queue"].clear()


def set_current(guild_id: int, track):
    get_state(guild_id)["current"] = track

