# Steam Backlog Tracker

A command-line tool to track and manage your Steam game backlog.

## Features

- Sync your Steam library with local caching
- Search for games by name
- Filter games by playtime (unplayed, under/over X hours, between ranges)
- Sort by name or playtime
- View library statistics with playtime distribution

## Setup

1. **Install dependencies:**
   ```bash
   pip install requests rich
   ```

2. **Run the tool:**
   ```bash
   python backlog.py
   ```
   On first run, the setup wizard will guide you through configuration.

   You'll need:
   - A Steam API key from https://steamcommunity.com/dev/apikey
   - Your 64-bit Steam ID from https://steamid.io

## Usage

**First sync:**
```bash
python backlog.py --sync
```

**View all games:**
```bash
python backlog.py
```

**Search for games:**
```bash
python backlog.py --search "dark souls"
```

**Filter options:**
```bash
python backlog.py --notplayed           # Never played
python backlog.py --started             # Started but barely played (0-2 hrs)
python backlog.py --under 5             # Under 5 hours
python backlog.py --over 50             # Over 50 hours
python backlog.py --between 10 50       # Between 10-50 hours
```

**Sort options:**
```bash
python backlog.py --sortby name
python backlog.py --sortby playtime
python backlog.py --sortby playtime-asc
```

**View statistics:**
```bash
python backlog.py --stats
```

**Reconfigure credentials:**
```bash
python backlog.py --setup
```

**Combine filters, search, and sorting:**
```bash
python backlog.py --notplayed --sortby name
python backlog.py --search "souls" --sortby playtime
python backlog.py --over 100 --sortby playtime
python backlog.py --between 1 10 --search "rpg"
```

## Privacy Settings

Your Steam profile and game details must be set to public for the library sync to work.

## Requirements

- Python 3.6+
- requests
- rich

## License

MIT License
