"""Steam API functions"""

import json
import sys
import requests
from rich.console import Console


def validate_credentials(api_key, steam_id):
    """Test credentials with a request to API"""
    url = (
        f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
        f"?key={api_key}&steamid={steam_id}&format=json"
    )
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return "response" in data
    except Exception:
        return False


def fetch_games(api_key, steam_id):
    """Fetch the user's game library from Steam API"""
    url = (
        f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
        f"?key={api_key}&steamid={steam_id}&format=json&include_appinfo=1"
    )

    console = Console()

    # check if API key is valid
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "response" not in data or "games" not in data["response"]:
            console.print(
                "Error: Unexpected response format from Steam API", style="red"
            )
            sys.exit(0)

        return data["response"]["games"]

    # checks if there is a network error
    except requests.exceptions.Timeout:
        console.print("Error: Steam API request timed out", style="red")
        console.print("Check your internet connection and try again", style="yellow")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        console.print("Error: Could not connect to Steam API", style="red")
        console.print("Check your internet connection and try again", style="yellow")
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response else 500
        if status_code == 401:
            console.print("Error: Invalid Steam API key", style="red")
        elif status_code == 403:
            console.print(
                "Error: Steam API request forbidden. Check your Steam profile privacy settings",
                style="red",
            )
        else:
            console.print(
                f"Error: Steam API request failed with status code {status_code}",
                style="red",
            )

        sys.exit(1)
    except json.JSONDecodeError:
        console.print("Error: Invalid response from Steam API", style="red")
        sys.exit(1)


def lookup_steam_game(appid):
    """Lookup game name from Steam Store API by App ID"""
    url = f"https://store.steampowered.com/api/appdetails?appids={appid}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        app_data = data.get(str(appid))
        if app_data and app_data.get("success"):
            return app_data.get("data", {}).get("name")
        return None
    except Exception:
        return None
