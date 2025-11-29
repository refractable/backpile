"""Cache and file storage functions"""

import json
import os
import sys

from datetime import datetime
from rich.console import Console

from . import CACHE_DIR, CACHE_FILE, TAGS_FILE, STATUS_FILE, MANUAL_GAMES_FILE


def ensure_cache():
    """Create cache directory if it doesn't exist"""
    try:
        if not os.path.exists(CACHE_DIR):
            os.mkdir(CACHE_DIR)
    except OSError as e:
        console = Console()
        console.print(f"Error creating cache directory: {e}", style="red")
        sys.exit(1)


def save_cache(games):
    """Save the user's game library to a cache file with timestamp"""
    ensure_cache()

    cache_data = {"last_updated": datetime.now().isoformat(), "games": games}

    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(cache_data, f, indent=2)
    except OSError as e:
        console = Console()
        console.print(f"Error saving cache file: {e}", style="red")
        sys.exit(1)


def load_cache():
    """Load the user's game library from a cache file if it exists"""
    if not os.path.exists(CACHE_FILE):
        return None

    console = Console()

    try:
        with open(CACHE_FILE) as f:
            cache_data = json.load(f)
    except json.JSONDecodeError:
        console.print(
            "Warning: Cache file is corrupted. Run --sync to rebuild", style="yellow"
        )
        return None
    except OSError as e:
        console.print(f"Error reading cache file: {e}", style="red")
        return None

    return cache_data


def load_tags():
    """Load tags from file"""
    if not os.path.exists(TAGS_FILE):
        return {}

    try:
        with open(TAGS_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_tags(tags):
    """Save tags to file"""
    ensure_cache()

    try:
        with open(TAGS_FILE, "w") as f:
            json.dump(tags, f, indent=2)
    except OSError as e:
        console = Console()
        console.print(f"Error saving tags: {e}", style="red")


def load_status():
    """Load manual status overrides from file"""
    if not os.path.exists(STATUS_FILE):
        return {}
    try:
        with open(STATUS_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_status(status):
    """Save manual status overrides to file"""
    ensure_cache()

    try:
        with open(STATUS_FILE, "w") as f:
            json.dump(status, f, indent=2)
    except OSError as e:
        console = Console()
        console.print(f"Error saving status: {e}", style="red")


def load_manual_games():
    """Load manually added games from file"""
    if not os.path.exists(MANUAL_GAMES_FILE):
        return []

    try:
        with open(MANUAL_GAMES_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_manual_games(games):
    """Save manually added games to file"""
    ensure_cache()
    try:
        with open(MANUAL_GAMES_FILE, "w") as f:
            json.dump(games, f, indent=2)
    except OSError as e:
        console = Console()
        console.print(f"Error saving manually added games: {e}", style="red")
