"""Export functions for game data"""

import csv
import json
from datetime import datetime

from backlog.cache import load_tags, load_status
from backlog.utils import get_game_status


def export_csv(games, filename="backlog.csv"):
    """Export games to CSV file"""

    tags = load_tags()
    manual_status = load_status()

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "Name",
                "AppID",
                "Playtime (hrs)",
                "Last Played",
                "Status",
                "Source",
                "Tags",
            ]
        )

        for game in games:
            hours = game["playtime_forever"] / 60
            appid = str(game["appid"])
            last_played = game.get("rtime_last_played", 0)

            if last_played > 0:
                last_played = datetime.fromtimestamp(last_played).strftime("%Y-%m-%d")
            else:
                last_played = "Never"

            status = get_game_status(game, manual_status)
            source = game.get("source", "Steam")
            game_tags = ", ".join(tags.get(appid, []))

            writer.writerow(
                [
                    game["name"],
                    appid,
                    f"{hours:.2f}",
                    last_played,
                    status,
                    source,
                    game_tags,
                ]
            )

    return filename


def export_json(games, filename="backlog.json"):
    """Export games to JSON file"""
    tags = load_tags()
    manual_status = load_status()

    export_data = []

    for game in games:
        hours = game["playtime_forever"] / 60
        appid = str(game["appid"])
        last_played = game.get("rtime_last_played", 0)

        if last_played > 0:
            last_played = datetime.fromtimestamp(last_played).strftime("%Y-%m-%d")
        else:
            last_played = None

        status = get_game_status(game, manual_status)
        source = game.get("source", "Steam")
        export_data.append(
            {
                "name": game["name"],
                "appid": game["appid"],
                "playtime_hours": round(hours, 2),
                "status": status,
                "source": source,
                "last_played": last_played,
                "tags": tags.get(appid, []),
            }
        )

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2)

    return filename
