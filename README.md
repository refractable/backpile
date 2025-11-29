# Steam Backlog Tracker

A command-line tool to track and manage your Steam game library. Pulls data directly from Steam's API and provides filtering, tagging, status tracking, and statistics.

## Features

- **Sync your Steam library** - Fetch games directly from Steam API
- **Filter games** - By playtime, status, tags, recently played, and more
- **Tag system** - Organize games with custom tags
- **Status tracking** - Auto-detects playing/backlog/dropped/inactive, with manual overrides for completed/hold
- **Manual game entries** - Track non-Steam games alongside your Steam library
- **Statistics** - View playtime distribution and library insights
- **Export** - Save filtered results to CSV or JSON

## Installation

```bash
git clone https://github.com/yourusername/steam-backlog-tracker.git
cd steam-backlog-tracker
pip install requests rich
```

## Setup

Run the tool and follow the interactive setup:

```bash
python main.py
```

You'll need:
1. **Steam API Key** - Get one at https://steamcommunity.com/dev/apikey
2. **Steam ID** - Find your 64-bit Steam ID at https://steamid.io

## Usage

### Basic Commands

```bash
# Sync library from Steam
python main.py --sync

# View all games
python main.py

# View library statistics
python main.py --stats
```

### Filtering

```bash
# Games never played
python main.py --notplayed

# Games under 5 hours
python main.py --under 5

# Games over 100 hours
python main.py --over 100

# Games between 10-50 hours
python main.py --between 10 50

# Barely started games (0-2 hours)
python main.py --started

# Recently played (last 2 weeks)
python main.py --recent

# Search by name
python main.py --search "dark souls"

# Filter by status
python main.py --filterstatus completed

# Filter by tag
python main.py --filter-tag rpg
```

### Sorting

```bash
python main.py --sortby name          # Alphabetical
python main.py --sortby playtime      # Most played first
python main.py --sortby playtime-asc  # Least played first
python main.py --sortby recent        # Recently played first
```

### Tags

```bash
# Add a tag
python main.py --tag "Dark Souls" rpg

# Remove a tag
python main.py --untag "Dark Souls" rpg

# View all tags
python main.py --tags

# Bulk tag multiple games
python main.py --bulktag coop "Portal 2" "Left 4 Dead" Terraria

# Bulk untag
python main.py --bulkuntag coop "Portal 2" "Left 4 Dead"
```

### Status Tracking

Games are automatically categorized based on activity:
- **playing** - Played in the last 2 weeks
- **backlog** - Never played
- **inactive** - Played but not recently
- **dropped** - Not played in 6+ months

Manual overrides for:
- **completed** - Finished games
- **hold** - Paused games

```bash
# Set status
python main.py --setstatus "Dark Souls" completed

# Bulk set status
python main.py --bulkstatus completed "Dark Souls" "Elden Ring" "Sekiro"

# Clear manual status (reverts to auto-detect)
python main.py --clearstatus "Dark Souls"
```

### Manual Games

Track non-Steam games or games from other platforms:

```bash
# Add by name
python main.py --addgame "God of War" --platform "PS5"

# Add by Steam App ID (auto-fetches name)
python main.py --addgame 105600 --platform "PC"

# Log playtime
python main.py --logtime "God of War" 5

# Remove a manual game
python main.py --removegame "God of War"

# Filter by source
python main.py --source steam    # Steam games only
python main.py --source manual   # Manual games only
```

### Export

```bash
# Export to CSV (respects filters)
python main.py --export csv

# Export games over 50 hours to JSON
python main.py --over 50 --export json
```

### Other Options

```bash
# Limit results
python main.py --notplayed --limit 10

# Reconfigure credentials
python main.py --setup
```

## Examples

```bash
# Find RPGs I haven't finished
python main.py --filter-tag rpg --filterstatus inactive

# Export my completed games
python main.py --filterstatus completed --export csv

# See what I've been playing lately
python main.py --recent --sortby playtime

# Find short games to clear from backlog
python main.py --notplayed --sortby playtime-asc --limit 20
```

## File Structure

```
main.py                 # Entry point
pyrightconfig.json      # Type checker config
backlog/
  __init__.py           # Package constants
  api.py                # Steam API functions
  cache.py              # Local data storage
  cli.py                # Command-line interface
  display.py            # Output formatting
  export.py             # CSV/JSON export
  utils.py              # Helper functions
```

Data is stored in `cache/`:
- `games.json` - Cached Steam library
- `tags.json` - Custom tags
- `status.json` - Manual status overrides
- `manual_games.json` - Non-Steam games

## Requirements

- Python 3.8+
- requests
- rich

## License

MIT
