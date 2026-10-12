# Thanks for:
### [@teleX](https://t.me/teleX) - 2505806
### [@DavideGalilei](https://t.me/DavideGalilei) - 239556789


# Technologies used:
### [MongoDB](https://www.mongodb.com/) - 5.0
### [Python](https://www.python.org/) - 3.10+
### [Telethon](https://pypi.org/project/Telethon/) - 1.45.0
### [PyMongo](https://pypi.org/project/pymongo/) - 4.18.3


# Running:
```sh
uv sync --locked                # runtime deps into .venv
cp config.py.example config.py  # fill API_ID, API_HASH, BOT_TOKEN, DB_URI
.venv/bin/python main.py
```


# Development:
```sh
uv sync --extra dev
uv run ruff check
uv run ruff format --check
uv run ty check
```

CI (`.github/workflows/ci.yml`) runs the same checks on every push and pull request.
