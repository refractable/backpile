"""Display functions for game data visualization"""

from datetime import datetime
from rich.console import Console
from rich.table import Table

from backlog.cache import load_tags, load_status
from backlog.utils import get_game_status


def display_games(games, title="Library", last_updated=None):
    """Display the user's game library"""
    console = Console()
    tags = load_tags()
    manual_status = load_status()

    has_manual = any(g.get("source") != "Steam" for g in games)

    table = Table(title=title)
    table.add_column("Game", justify="left", style="green", no_wrap=False)
    table.add_column("Playtime", justify="right", style="cyan")
    table.add_column("Status", justify="left", style="magenta")

    if has_manual:
        table.add_column("Source", justify="left", style="blue")

    if tags:
        table.add_column("Tags", justify="left", style="yellow")

    # checks hours played and displays it
    for game in games:
        hours = game["playtime_forever"] / 60
        appid = str(game["appid"])
        game_tags = tags.get(appid, [])
        status = get_game_status(game, manual_status)
        source = game.get("source", "Steam")

        row = [game["name"], f"{hours:.2f} hours", status]
        if has_manual:
            row.append(source)
        if tags:
            row.append(", ".join(game_tags))

        table.add_row(*row)

    console.print(table)
    console.print(f"\nTotal games: {len(games)}", style="dim")

    # self explanatory i think
    if last_updated:
        dt = datetime.fromisoformat(last_updated)
        console.print(f"Last synced: {dt.strftime('%Y-%m-%d %H:%M:%S')}", style="dim")


def display_all_tags(games):
    """Display all tags and their game counts"""
    console = Console()
    tags = load_tags()

    if not tags:
        console.print("No tags found. Use --tag to add tags to games", style="yellow")
        return

    tag_games = {}
    games_by_id = {str(g["appid"]): g["name"] for g in games}

    for appid, game_tags in tags.items():
        for tag in game_tags:
            if tag not in tag_games:
                tag_games[tag] = []

            game_name = games_by_id.get(appid, f"Unknown ({appid})")
            tag_games[tag].append(game_name)

    table = Table(title="Tags")
    table.add_column("Tag", style="yellow")
    table.add_column("Count", justify="right", style="cyan")
    table.add_column("Games", style="green")

    for tag in sorted(tag_games.keys()):
        game_list = tag_games[tag]
        preview = ", ".join(game_list[:3])
        if len(game_list) > 3:
            preview += f" (+{len(game_list) - 3} more)"

        table.add_row(tag, str(len(game_list)), preview)

    console.print(table)


def display_stats(games):
    """Display stats about the user's game library"""
    console = Console()

    # total games, total playtime, not played games
    total_games = len(games)
    total_minutes = sum(g["playtime_forever"] for g in games)
    total_hours = total_minutes / 60

    not_played = [g for g in games if g["playtime_forever"] == 0]
    not_played_count = len(not_played)
    not_played_percent = (
        (not_played_count / total_games * 100) if total_games > 0 else 0
    )

    played_games = [g for g in games if g["playtime_forever"] > 0]
    avg_hours = (
        (sum(g["playtime_forever"] for g in played_games) / 60 / len(played_games))
        if played_games
        else 0
    )

    most_played = max(games, key=lambda g: g["playtime_forever"]) if games else None
    least_played = (
        min(played_games, key=lambda g: g["playtime_forever"]) if played_games else None
    )

    brackets = [
        ("Never played", lambda h: h == 0),
        ("Under 1 hour", lambda h: 0 < h < 1),
        ("1-10 hours", lambda h: 1 <= h < 10),
        ("10-50 hours", lambda h: 10 <= h < 50),
        ("50-100 hours", lambda h: 50 <= h < 100),
        ("100+ hours", lambda h: h >= 100),
    ]

    # initialize table
    table = Table(title="Library Statistics", show_header=False)
    table.add_column("Statistic", style="cyan")
    table.add_column("Value", justify="right", style="green")

    table.add_row("Total Games", str(total_games))
    table.add_row("Total Playtime", f"{total_hours:.2f} hours")
    table.add_row("Not Played Games", f"{not_played_count} ({not_played_percent:.2f}%)")
    table.add_row("Played Games", str(len(played_games)))

    if played_games:
        table.add_row("Average Playtime", f"{avg_hours:.2f} hours")

    if most_played:
        most_played_hours = most_played["playtime_forever"] / 60
        table.add_row(
            "Most Played", f"{most_played['name']} ({most_played_hours:.2f} hrs)"
        )

    if least_played:
        least_played_hours = least_played["playtime_forever"] / 60
        table.add_row(
            "Least Played", f"{least_played['name']} ({least_played_hours:.2f} hrs)"
        )

    console.print(table)

    # playtime distribution table for additional insight
    console.print()
    console.print("[bold]Playtime Distribution[/bold]")
    console.print()

    bracket_data = []

    for label, condition in brackets:
        count = len([g for g in games if condition(g["playtime_forever"] / 60)])
        percent = (count / total_games * 100) if total_games else 0
        bracket_data.append((label, count, percent))

    max_height = 12
    max_percent = max(b[2] for b in bracket_data) if bracket_data else 1

    for row in range(max_height, 0, -1):
        line = "    "
        for label, count, percent in bracket_data:
            bar_height = (
                int((percent / max_percent) * max_height) if max_percent > 0 else 0
            )
            if row <= bar_height:
                line += " [yellow]██[/yellow]    "
            else:
                line += "       "

        console.print(line)

    console.print("  " + "───────" * len(bracket_data))

    pct_line = " "

    for label, count, percent in bracket_data:
        pct_line += f" [green]{percent:4.0f}%[/green] "

    console.print(pct_line)
    short_labels = [" 0 hr", " <1 hr", "1-10", "10-50", "50-100", "100+"]
    label_line = " "

    for short in short_labels:
        label_line += f" [cyan]{short:^5}[/cyan] "

    console.print(label_line)

    # status summary
    console.print()
    console.print("[bold]Status Summary[/bold]")

    manual_status = load_status()
    status_counts = {
        "playing": 0,
        "backlog": 0,
        "inactive": 0,
        "dropped": 0,
        "completed": 0,
        "hold": 0,
    }

    for game in games:
        status = get_game_status(game, manual_status)
        status_counts[status] = status_counts.get(status, 0) + 1

    status_table = Table(show_header=False)
    status_table.add_column("Status", style="magenta")
    status_table.add_colum("Count", justify="right", style="green")

    for status_name, count in status_counts.items():
        if count > 0:
            status_table.add_row(status_name.capitalize(), str(count))

    console.print(status_table)
