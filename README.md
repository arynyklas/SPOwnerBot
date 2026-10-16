# Thanks for:
### [@teleX](https://t.me/teleX)
### [@DavideGalilei](https://t.me/DavideGalilei)
### [@madrik1337](https://t.me/madrik1337)


# Technologies used:
### [MongoDB](https://www.mongodb.com/) - 8.0
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


# Docker:
```sh
cp config.py.example config.py  # fill API_ID, API_HASH, BOT_TOKEN; DB_URI = "mongodb://mongo:27017"
docker compose up -d --build
docker compose logs -f bot
```

The image carries no secrets: compose mounts the project directory read-only and the bot reads `config.py` from it, so `docker compose restart bot` applies an edit. The file must be readable by the container's uid 65532 (`cp` leaves it world-readable).

MongoDB publishes no ports; its data lives in the `spownerbot_mongo-data` volume, the Telethon session in `spownerbot_session`.
```sh
docker compose exec mongo mongosh SPOwnerBot                                         # shell
docker compose exec -T mongo mongodump --archive --gzip --db SPOwnerBot > backup.gz   # backup
docker compose exec -T mongo mongorestore --archive --gzip < backup.gz                # restore
```


# Checks:
```sh
uv run ruff check
uv run ruff format --check
uv run ty check
```

CI (`.github/workflows/ci.yml`) runs the same checks on every push and pull request.
