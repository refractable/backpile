"""Utility functions for game data manipulation"""

import time
from .cache import load_manual_games


def get_game_status(game, manual_status=None):
    """Calculate game status if its manually overriden or auto detected"""
    import time

    appid = str(game["appid"])

    if manual_status and appid in manual_status:
        return manual_status[appid]

    playtime = game.get("playtime_forever", 0)
    playtime_2weeks = game.get("playtime_2weeks", 0)
    last_played = game.get("rtime_last_played", 0)

    if playtime_2weeks > 0:
        return "playing"

    if playtime == 0:
        return "backlog"

    six_months_ago = time.time() - (180 * 24 * 60 * 60)
    if last_played > 0 and last_played < six_months_ago:
        return "dropped"

    return "inactive"


def get_next_manual_id():
    """Generate next manual game ID"""
    games = load_manual_games()
    if not games:
        return "manual_1"

    max_id = 0
    for game in games:
        if game.get("appid", "").startswith("manual_"):
            try:
                num = int(game["appid"].split("_")[1])
                max_id = max(max_id, num)
            except (ValueError, IndexError):
                pass
    return f"manual_{max_id + 1}"


def merge_games(steam_games, manual_games):
    """Merge steam and manual games into one list"""
    for game in steam_games:
        game["source"] = "Steam"
    for game in manual_games:
        game["source"] = game.get("platform", "Manual")

    return steam_games + manual_games


def find_game_by_name(games, search_term):
    """Find game by partial name match"""
    search_lower = search_term.lower()

    for game in games:
        if game["name"].lower() == search_lower:
            return game

    matches = [g for g in games if search_lower in g["name"].lower()]

    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        return matches

    return None
