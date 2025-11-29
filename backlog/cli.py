"""Command line interface for Steam Backlog Tracker"""

import argparse
import json
import os
import sys
import time as time_module
from datetime import datetime
from rich.console import Console

from backlog.api import fetch_games, validate_credentials, lookup_steam_game
from backlog.cache import (
    load_cache,
    save_cache,
    load_tags,
    save_tags,
    load_status,
    save_status,
    load_manual_games,
    save_manual_games

)
from backlog.display import display_games, display_all_tags, display_stats
from backlog.export import export_csv, export_json
from backlog.utils import find_game_by_name, get_game_status, get_next_manual_id, merge_games


def setup_config():
    """Setup for creating config"""
    console = Console()

    console.print("\n[bold cyan]Steam Backlog Tracker Setup[/bold cyan]\n")
    console.print("To use this tool, you'll need a Steam API key and your Steam ID.\n")
    console.print("[bold]Step 1: Steam API key[/bold]")
    console.print("Get your key at: https://steamcommunity.com/dev/apikey", style="dim")

    api_key = input("Enter your Steam API key: ").strip()

    if not api_key:
        console.print("Error: API key cannot be empty", style="red")
        sys.exit(1)

    console.print("\n[bold]Step 2: Steam ID[/bold]")
    console.print("Find your 64-bit tem ID at: https://steamid.io", style="dim")
    steam_id = input("Enter your Steam ID: ").strip()

    if not steam_id:
        console.print("Error: Steam ID cannot be empty", style="red")
        sys.exit(1)

    console.print("\nValidating credentials..", style="dim")

    if validate_credentials(api_key, steam_id):
        console.print("Credentials are valid. Saving config..", style="green")
    else:
        console.print("Warning: Could not validate credentials", style="yellow")
        console.print(
            "This could mean invalid API key, private profile, or network issues.",
            style="dim",
        )
        confirm = input("Save anyway? (y/n): ").strip().lower()

        if confirm != "y":
            console.print("Setup cancelled. Exiting..", style="red")
            sys.exit(1)

    config = {"API_KEY": api_key, "STEAM_ID": steam_id}

    try:
        with open("config.json", "w") as f:
            json.dump(config, f, indent=2)
        console.print("\nConfig saved to config.json", style="green")
        console.print(
            "Run 'python backlog.py --sync' to fetch your game library\n", style="dim"
        )
    except OSError as e:
        console.print(f"Error saving config: {e}", style="red")
        sys.exit(1)

    return config


def load_config():

    console = Console()

    if not os.path.exists("config.json"):
        return setup_config()

    try:
        with open("config.json") as f:
            config = json.load(f)
    except json.JSONDecodeError:
        console.print("Error: config.json is corrupted or invalid", style="red")
        console.print("Delete config.json and run again to start fresh", style="yellow")
        sys.exit(1)

    if "API_KEY" not in config or "STEAM_ID" not in config:
        console.print("Error: config.json is missing required keys", style="red")
        console.print("Delete config.json and run again to start fresh", style="yellow")
        sys.exit(1)

    return config


def main():

    # initializing parser
    parser = argparse.ArgumentParser(description="Steam game backlog tracker")
    parser.add_argument(
        "--notplayed",
        action="store_true",
        help="Display games that have not been played",
    )
    parser.add_argument(
        "--under", type=float, help="Display games that have less than X hours played"
    )
    parser.add_argument(
        "--over", type=float, help="Display games hat have more than X hours played"
    )
    parser.add_argument(
        "--between",
        nargs=2,
        type=float,
        metavar=("MIN", "MAX"),
        help="Display games that have between MIN and MAX hours played",
    )
    parser.add_argument(
        "--started",
        action="store_true",
        help="Display games started but barely played (0-2hrs)",
    )
    parser.add_argument(
        "--recent",
        action="store_true",
        help="Display recently played games in the last two weeks",
    )
    parser.add_argument(
        "--sync", action="store_true", help="Sync the game library from Steam"
    )
    parser.add_argument(
        "--sortby",
        choices=["name", "playtime", "playtime-asc", "recent"],
        help="Sort games by name or playtime",
    )
    parser.add_argument(
        "--stats", action="store_true", help="Display library statistics"
    )
    parser.add_argument(
        "--setup", action="store_true", help="Run setup wizard to configure credentials"
    )
    parser.add_argument("--search", type=str, help="Search for a game by name")
    # tag arguments
    parser.add_argument(
        "--tag", nargs=2, metavar=("GAME", "TAG"), help="Add a tag to a game"
    )
    parser.add_argument(
        "--untag", nargs=2, metavar=("GAME", "TAG"), help="Remove a tag from a game"
    )
    parser.add_argument("--tags", action="store_true", help="Display all tags")
    parser.add_argument(
        "--filter-tag", type=str, metavar="TAG", help="Filter games by tag"
    )
    parser.add_argument(
        "--bulktag",
        nargs="+",
        metavar="ARGS",
        help="Add tag to multiple games: --bulktag TAG GAME1 GAME2 ...",
    )
    parser.add_argument(
        "--bulkuntag",
        nargs="+",
        metavar="ARGS",
        help="Remove tag from multiple games: --bulkuntag TAG GAME1 GAME2 ...",
    )
    parser.add_argument("--limit", type=int, help="Limit number of games to display")
    parser.add_argument(
        "--export",
        choices=["csv", "json"],
        help="Export games to file (respects filters)",
    )

    # status arguments
    parser.add_argument(
        "--setstatus",
        nargs=2,
        metavar=("GAME", "STATUS"),
        help="Set game status (completed/hold)",
    )
    parser.add_argument(
        "--clearstatus", type=str, metavar="GAME", help="Clear manual status override"
    )
    parser.add_argument(
        "--filterstatus",
        type=str,
        choices=["playing", "backlog", "dropped", "inactive", "completed", "hold"],
        help="Filter by status",
    )
    parser.add_argument(
        "--bulkstatus",
        nargs="+",
        metavar="ARGS",
        help="Set status for multiple games: --bulkstatus STATUS GAME1 GAME2 ...",
    )

    # manual games arguments
    parser.add_argument(
        "--addgame", type=str, metavar="NAME", help="Add a non-Steam game"
    )
    parser.add_argument(
        "--platform",
        type=str,
        default="Other",
        help="Platform for manual game (use with --addgame)",
    )
    parser.add_argument(
        "--logtime",
        nargs=2,
        metavar=("GAMES", "HOURS"),
        help="Log playtime for manual games",
    )
    parser.add_argument(
        "--removegame", type=str, metavar="NAME", help="Remove a manually added game"
    )
    parser.add_argument(
        "--source",
        choices=["steam", "manual", "all"],
        default="all",
        help="Filter by game source",
    )

    args = parser.parse_args()

    config = load_config()

    # first time setup / reconfigure setup
    if args.setup:
        if os.path.exists("config.json"):
            console = Console()
            confirm = (
                input("config.json already exists. Overwrite? (y/n): ").strip().lower()
            )

            if confirm != "y":
                console.print("Setup cancelled", style="yellow")
                return

        setup_config()
        return

    if args.addgame:
        console = Console()
        manual_games = load_manual_games()

        if args.addgame.isdigit():
            appid = args.addgame
            console.print(f"Looking up Steam AppID {appid}...", style="dim")
            game_name = lookup_steam_game(appid)

            if not game_name:
                console.print(f"Could not find game with AppID {appid}", style="red")
                return

            for game in manual_games:
                if (
                    str(game.get("appid")) == appid
                    or game["name"].lower() == game_name.lower()
                ):
                    console.print(
                        f"'{game_name}' already exists in manual games", style="yellow"
                    )
                    return

            new_game = {
                "appid": appid,
                "name": game_name,
                "platform": args.platform,
                "playtime_forever": 0,
                "rtime_last_played": 0,
                "playtime_2weeks": 0,
            }
            manual_games.append(new_game)
            save_manual_games(manual_games)
            console.print(
                f"Added '{game_name}' (App ID: {appid}, {args.platform})", style="green"
            )
            return

        for game in manual_games:
            if game["name"].lower() == args.addgame.lower():
                console.print(
                    f"{args.addgame} already exists in manual games", style="yellow"
                )
                return
        new_game = {
            "appid": get_next_manual_id(),
            "name": args.addgame,
            "platform": args.platform,
            "playtime_forever": 0,
            "rtime_last_played": 0,
            "playtime_2weeks": 0,
        }
        manual_games.append(new_game)
        save_manual_games(manual_games)
        console.print(f"Added '{args.addgame}' ({args.platform})", style="green")
        return

    if args.removegame:
        console = Console()
        manual_games = load_manual_games()

        found = None
        for game in manual_games:
            if game["name"].lower() == args.removegame.lower():
                found = game
                break

        if not found:
            console.print(f"No game found matching '{args.removegame}'", style="red")
            console.print(
                f"Note: Steam games cannot be removed, only manual entries.",
                style="dim",
            )
            return

        manual_games.remove(found)
        save_manual_games(manual_games)
        console.print(f"Removed '{found['name']}'", style="green")
        return

    if args.logtime:
        game_name, hours_str = args.logtime
        try:
            hours = float(hours_str)
        except ValueError:
            console = Console()
            console.print(f"Invalid hours: {hours_str}", style="red")
            return
        console = Console()
        manual_games = load_manual_games()

        found = None
        for game in manual_games:
            if game["name"].lower() == game_name.lower():
                found = game
                break
        if not found:
            console.print(f"No manual game found matching '{game_name}'", style="red")
            console.print(f"Note: Steam games are tracked automatically", style="dim")
            return

        import time as time_module

        found["playtime_forever"] += int(hours * 60)
        found["rtime_last_played"] = int(time_module.time())
        save_manual_games(manual_games)

        total_hours = found["playtime_forever"] / 60
        console.print(
            f"Logged {hours} hours for '{game_name}' ({total_hours:.2f} hours total)",
            style="green",
        )
        return

    # tag management
    if args.tag or args.untag or args.tags:
        cache_data = load_cache()

        if cache_data is None:
            console = Console()
            console.print("No cache found. Use --sync first", style="red")
            return

        games = cache_data["games"]
        manual_games = load_manual_games()
        games = merge_games(games, manual_games)

        if args.tags:
            display_all_tags(games)
            return

        if args.tag:
            game_name, tag_name = args.tag
            result = find_game_by_name(games, game_name)
            console = Console()

            if result is None:
                console.print(f"No game found matching '{game_name}'", style="red")
                return
            elif isinstance(result, list):
                console.print(f"Multiple games match '{game_name}':", style="yellow")

                for g in result[:10]:
                    console.print(f" - {g['name']}", style="dim")
                return

            tags = load_tags()
            appid = str(result["appid"])

            if appid not in tags:
                tags[appid] = []
            if tag_name not in tags[appid]:
                tags[appid].append(tag_name)
                save_tags(tags)
                console.print(
                    f"Added tag '{tag_name}' to {result['name']}", style="green"
                )
            else:
                console.print(
                    f"{result['name']} already has tag '{tag_name}'", style="yellow"
                )
            return

        if args.untag:
            game_name, tag_name = args.untag
            result = find_game_by_name(games, game_name)
            console = Console()

            if result is None:
                console.print(f"No game found matching '{game_name}'", style="red")
                return

            elif isinstance(result, list):
                console.print(f"Multiple games match '{game_name}':", style="yellow")

                for g in result[:10]:
                    console.print(f" - {g['name']}", style="dim")
                return

            tags = load_tags()
            appid = str(result["appid"])

            if appid in tags and tag_name in tags[appid]:
                tags[appid].remove(tag_name)

                if not tags[appid]:
                    del tags[appid]

                save_tags(tags)
                console.print(
                    f"Removed tag '{tag_name}' from {result['name']}", style="green"
                )
            else:
                console.print(
                    f"{result['name']} doesn't have tag '{tag_name}'", style="yellow"
                )

            return

    # bulk tag management (pain)
    if args.bulktag or args.bulkuntag:
        cache_data = load_cache()

        if cache_data is None:
            console = Console()
            console.print("No cache found. Use --sync first", style="red")
            return

        games = cache_data["games"]
        manual_games = load_manual_games()
        games = merge_games(games, manual_games)
        console = Console()

        if args.bulktag:
            if len(args.bulktag) < 2:
                console.print("Usage: --bulktag TAG GAME1 GAME2 GAME3 ...", style="red")
                return

            tag_name = args.bulktag[0]
            game_names = args.bulktag[1:]
            tags = load_tags()
            success_count = 0

            for game_name in game_names:
                result = find_game_by_name(games, game_name)

                if result is None:
                    console.print(f"  No game found: '{game_name}'", style="red")
                elif isinstance(result, list):
                    console.print(f"  Multiple matches: '{game_name}'", style="yellow")
                else:
                    appid = str(result["appid"])
                    if appid not in tags:
                        tags[appid] = []
                    if tag_name not in tags[appid]:
                        tags[appid].append(tag_name)
                        console.print(f"  Tagged: {result['name']}", style="green")
                        success_count += 1
                    else:
                        console.print(
                            f"  Already tagged: {result['name']}", style="dim"
                        )
            save_tags(tags)
            console.print(
                f"\nAdded tag '{tag_name}' to {success_count} game(s)",
                style="bold_green",
            )
            return

        if args.bulkuntag:
            if len(args.bulkuntag) < 2:
                console.print("Usage: --bulkuntag TAG GAME1 GAME2 ...", style="red")
                return

            tag_name = args.bulkuntag[0]
            game_names = args.bulkuntag[1:]
            tags = load_tags()
            success_count = 0

            for game_name in game_names:
                result = find_game_by_name(games, game_name)

                if result is None:
                    console.print(f"  No game found: '{game_name}'", style="red")
                elif isinstance(result, list):
                    console.print(f"  Multiple matches: '{game_name}'", style="yellow")
                else:
                    appid = str(result["appid"])
                    if appid in tags and tag_name in tags[appid]:
                        tags[appid].remove(tag_name)
                        if not tags[appid]:
                            del tags[appid]
                        console.print(f"  Untagged: {result['name']}", style="green")
                        success_count += 1
                    else:
                        console.print(f"  No such tag: {result['name']}", style="dim")

            save_tags(tags)
            console.print(
                f"\nRemoved '{tag_name}' from {success_count} game(s)",
                style="bold green",
            )
            return

    # status management
    if args.setstatus or args.clearstatus:
        cache_data = load_cache()

        if cache_data is None:
            console = Console()
            console.print("No cache found. Use --sync first", style="red")
            return

        games = cache_data["games"]
        if args.setstatus:

            game_name, new_status = args.setstatus

            if new_status not in ["completed", "hold"]:
                console = Console()
                console.print(
                    "Manual status must be 'completed' or 'hold'", style="red"
                )
                console.print(
                    "Other statuses (playing, backlog, dropped) are auto-detected",
                    style="dim",
                )
                return

            result = find_game_by_name(games, game_name)
            console = Console()

            if result is None:
                console.print(f"No game found matching '{game_name}'", style="red")
                return
            elif isinstance(result, list):
                console.print(f"Multiple games match '{game_name}':", style="yellow")

                for g in result[:10]:
                    console.print(f"  - {g['name']}", style="dim")

                return

            status = load_status()
            appid = str(result["appid"])
            status[appid] = new_status
            save_status(status)
            console.print(
                f"Set {result['name']} status to '{new_status}'", style="green"
            )
            return

        if args.clearstatus:
            result = find_game_by_name(games, args.clearstatus)
            console = Console()

            if result is None:
                console.print(
                    f"No game found matching '{args.clearstatus}'", style="red"
                )
                return
            elif isinstance(result, list):
                console.print(
                    f"Multiple games match '{args.clearstatus}':", style="yellow"
                )

                for g in result[:10]:
                    console.print(f"  - {g['name']}", style="dim")
                return

            status = load_status()
            appid = str(result["appid"])

            if appid in status:
                del status[appid]
                save_status(status)
                console.print(
                    f"Cleared status for {result['name']} (will auto-detect)",
                    style="green",
                )
            else:
                console.print(
                    f"{result['name']} has no manual status override", style="yellow"
                )
            return
    # bulk status management
    if args.bulkstatus:
        if len(args.bulkstatus) < 2:
            console = Console()
            console.print("Usage: --bulkstatus STATUS GAME1 GAME2 ...", style="red")
            return

        new_status = args.bulkstatus[0]
        game_names = args.bulkstatus[1:]

        if new_status not in ["completed", "hold"]:
            console = Console()
            console.print(f"Manual status must be 'completed' or 'hold'", style="red")
            console.print(
                "Other statuses (playing, backlog, dropped) are auto-detected",
                style="dim",
            )
            return

        cache_data = load_cache()

        if cache_data is None:
            console = Console()
            console.print("No cache found. Use --sync first", style="red")
            return

        games = cache_data["games"]
        manual_games = load_manual_games()
        games = merge_games(games, manual_games)
        console = Console()
        status = load_status()
        success_count = 0

        for game_name in game_names:
            result = find_game_by_name(games, game_name)

            if result is None:
                console.print(f"  No game found: '{game_name}'", style="red")
            elif isinstance(result, list):
                console.print(f"  Multiple matches: '{game_name}'", style="yellow")
            else:
                appid = str(result["appid"])
                status[appid] = new_status
                console.print(f"  Set status: {result['name']}", style="green")
                success_count += 1

        save_status(status)
        console.print(
            f"\nSet '{new_status}' for {success_count} game(s)", style="green"
        )
        return

    # syncing, checks if user has cache already or not
    if args.sync:
        console = Console()
        console.print("Syncing game library from Steam...", style="dim")
        games = fetch_games(config["API_KEY"], config["STEAM_ID"])

        save_cache(games)

        console.print("Games synced successfully!", style="green")
        last_updated = datetime.now().isoformat()
    else:

        cache_data = load_cache()

        if cache_data is None:
            console = Console()
            console.print(
                "No cache found. Use --sync to sync the game library from Steam.",
                style="red",
            )
            return

        games = cache_data["games"]
        last_updated = cache_data["last_updated"]

    manual_games = load_manual_games()
    games = merge_games(games, manual_games)

    if args.source == "steam":
        games = [g for g in games if g.get("source") == "Steam"]
    elif args.source == "manual":
        games = [g for g in games if g.get("source") != "Steam"]

    # statistics
    if args.stats:
        display_stats(games)
        return

    # filtering
    if args.search:
        search_term = args.search.lower()
        games = [g for g in games if search_term in g["name"].lower()]

    if args.filter_tag:
        tags = load_tags()
        games = [g for g in games if args.filter_tag in tags.get(str(g["appid"]), [])]

    if args.filterstatus:
        manual_status = load_status()
        games = [
            g for g in games if get_game_status(g, manual_status) == args.filterstatus
        ]

    if args.notplayed:
        games = [g for g in games if g["playtime_forever"] == 0]
    elif args.started:
        games = [g for g in games if g["playtime_forever"] / 60 <= 2]
    elif args.recent:
        games = [g for g in games if g.get("playtime_2weeks", 0) > 0]
    elif args.under:
        games = [g for g in games if g["playtime_forever"] / 60 < args.under]
    elif args.over:
        games = [g for g in games if g["playtime_forever"] / 60 > args.over]
    elif args.between:
        min_hrs, max_hrs = args.between
        games = [g for g in games if min_hrs <= g["playtime_forever"] / 60 <= max_hrs]

    # sorting

    if args.sortby == "name":
        games = sorted(games, key=lambda g: g["name"].lower())
    elif args.sortby == "playtime":
        games = sorted(games, key=lambda g: g["playtime_forever"], reverse=True)
    elif args.sortby == "playtime-asc":
        games = sorted(games, key=lambda g: g["playtime_forever"])
    elif args.sortby == "recent":
        games = sorted(games, key=lambda g: g.get("rtime_last_played", 0), reverse=True)

    # title labeling

    if args.search:
        title = f"Search results for {args.search}"
    elif args.filter_tag:
        title = f"Tag: {args.filter_tag}"
    elif args.filterstatus:
        title = f"Status: {args.filterstatus}"
    elif args.notplayed:
        title = "Not played games"
    elif args.started:
        title = "Started but barely played games (0-2hrs)"
    elif args.recent:
        title = f"Recently played (last 2 weeks)"
    elif args.under:
        title = f"Games under {args.under} hours"
    elif args.over:
        title = f"Games over {args.over} hours"
    elif args.between:
        title = f"Games between {args.between[0]}-{args.between[1]} hours"
    else:
        title = "Library"

    # limits # of games displayed
    if args.limit:
        games = games[: args.limit]

    if args.export:
        console = Console()

        if args.export == "csv":
            filename = export_csv(games)
            console.print(f"Exported {len(games)} games to {filename}", style="green")
        elif args.export == "json":
            filename = export_json(games)
            console.print(f"Exported {len(games)} games to {filename}", style="green")
        return

    display_games(games, title, last_updated=last_updated)


if __name__ == "__main__":
    main()
