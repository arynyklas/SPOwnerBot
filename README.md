# Thanks for:
### [@teleX](https://t.me/teleX)
### [@DavideGalilei](https://t.me/DavideGalilei)
### [@madrik1337](https://t.me/madrik1337)


# Technologies used:
### [MongoDB](https://www.mongodb.com/) - 5.0
### [Python](https://www.python.org/) - 3.10+
### [Telethon](https://pypi.org/project/Telethon/) - 1.45.0
### [PyMongo](https://pypi.org/project/pymongo/) - 4.18.3


# Setup:
```sh
uv sync --locked --extra dev    # drop --extra dev on servers
cp config.py.example config.py  # fill API_ID, API_HASH, BOT_TOKEN, DB_URI
```


# Running:
```sh
.venv/bin/python main.py
```


# Checks:
```sh
uv run ruff check
uv run ruff format --check
uv run ty check
```

CI (`.github/workflows/ci.yml`) runs the same checks on every push and pull request.
