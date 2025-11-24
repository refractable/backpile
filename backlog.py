import requests
import json
import argparse
from rich.console import Console
from rich.table import Table


def pull_games(api_key, steam_id):

    url = (
        f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
        f"?key={api_key}&steamid={steam_id}&format=json&include_appinfo=1"
    )
    response = requests.get(url)

    return response.json()['response']['games']


def display_games(games, title="Library"):

    console = Console()

    table = Table(title=title)
    table.add_column("Game", justify="left", style="cyan", no_wrap=False)
    table.add_column("Playtime", justify="right", style="green")

    for game in games:
        hours = game["playtime_forever"] / 60
        table.add_row(game["name"], f"{hours:.2f} hours")

    console.print(table)
    console.print(f"\nTotal games: {len(games)}")


def main():

    parser = argparse.ArgumentParser(description="Steam game backlog tracker")
    parser.add_argument('--notplayed', action='store_true', help='Display games that have not been played')
    parser.add_argument('--under', type=float, help="Display games that have less than X hours played")
    args = parser.parse_args()

    with open("config.json") as f:
        config = json.load(f)

    games = pull_games(config["API_KEY"], config["STEAM_ID"])

    if args.notplayed:
        games = [g for g in games if g['playtime_forever'] == 0]
        display_games(games, "Not played")

    elif args.under:
        games = [g for g in games if g['playtime_forever'] / 60 < args.under]
        display_games(games, f"Under {args.under} hours")

    else:
        display_games(games)


if __name__ == "__main__":
    main()
