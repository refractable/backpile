<h1 align="center">Contributing to Backpile</h1>

<p align="center">
  Thanks for your interest in contributing!
</p>

<p align="center">
  <a href="#getting-started">Getting Started</a> •
  <a href="#development">Development</a> •
  <a href="#submitting-changes">Submitting Changes</a> •
  <a href="#ideas">Ideas</a>
</p>

---

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/backpile.git
   cd backpile
   ```
3. Install dependencies:
   ```bash
   pip install requests rich
   ```
4. Run `python main.py` and follow the setup wizard

## Development

### Project Structure

```
backpile/
├── main.py              # Entry point
├── backlog/
│   ├── __init__.py      # Constants
│   ├── api.py           # Steam API
│   ├── cache.py         # Data storage
│   ├── cli.py           # CLI interface
│   ├── display.py       # Output formatting
│   ├── export.py        # CSV/JSON export
│   └── utils.py         # Helpers
└── ...
```

### Code Style

- Use [Black](https://github.com/psf/black) for formatting
- Add docstrings to new functions
- Keep functions focused and reasonably sized

## Submitting Changes

1. Create a branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes
3. Test thoroughly
4. Commit with clear messages:
   ```bash
   git commit -m "Add feature: description"
   ```
5. Push and open a Pull Request

### Pull Request Guidelines

- Keep PRs focused on a single feature or fix
- Update README if adding new commands
- Test with your own Steam library before submitting

## Ideas

Areas where contributions are welcome:

- New filters or sorting options
- Display improvements
- Documentation and examples
- Bug fixes (check Issues tab)
- Tests

---

<p align="center">
  Questions? Open an issue with the <b>Question</b> template.
</p>
