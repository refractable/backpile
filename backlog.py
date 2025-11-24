import requests
import json
from rich.console import Console
from rich.table import Table

with open("config.json") as f:
    config = json.load(f)


API_KEY = config["API_KEY"]
STEAM_ID = config["STEAM_ID"]


url = (
    f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
    f"?key={API_KEY}&steamid={STEAM_ID}&format=json&include_appinfo=1"
)


response = requests.get(url)
data = response.json()
console = Console()


table = table = Table(title="My Steam Backlog")
table.add_column("Game", justify="left", style="cyan", no_wrap=False)
table.add_column("Playtime", justify="right", style="green")


games = data["response"]["games"]


for game in games:
    hours = game["playtime_forever"] / 60
    table.add_row(game["name"], f"{hours:.2f} hours")


console.print(table)
