"""Steam Backlog Tracker - Track and manage your Steam game library"""
import os

CACHE_DIR = "cache"
CACHE_FILE = os.path.join(CACHE_DIR, "games.json")
TAGS_FILE = os.path.join(CACHE_DIR, "tags.json")
STATUS_FILE = os.path.join(CACHE_DIR, "status.json")
MANUAL_GAMES_FILE = os.path.join(CACHE_DIR, "manual_games.json")
