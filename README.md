# Thanks for:
### [@teleX](https://t.me/teleX)
### [@DavideGalilei](https://t.me/DavideGalilei)
### [@madrik1337](https://t.me/madrik1337)


# Technologies used:
### [MongoDB](https://www.mongodb.com/) - 8.0
### [Python](https://www.python.org/) - 3.13
### [Telethon](https://pypi.org/project/Telethon/) - 1.45.0
### [PyMongo](https://pypi.org/project/pymongo/) - 4.18.3


# Setup:
```sh
uv sync --locked --extra dev        # drop --extra dev on servers
cp config.json.example config.json  # fill api_id, api_hash, bot_token, db_uri, db_name
```


# Configuration:
The bot reads one JSON file at start-up: the path in `SPOWNERBOT_CONFIG`, else `/etc/spownerbot/config.json`. All five keys are required:

| Key | Type | Value |
|---|---|---|
| `api_id` | integer | Telegram API ID |
| `api_hash` | string | Telegram API hash |
| `bot_token` | string | bot token from @BotFather |
| `db_uri` | string | MongoDB connection URI |
| `db_name` | string | MongoDB database name |

A missing or mistyped key stops the bot with an error that names the key but never its value.

Logs are JSON, one object per line on stdout: `ts` (UTC), `level`, `logger`, `msg`, and `exc` for tracebacks.


# Running:
```sh
SPOWNERBOT_CONFIG=config.json .venv/bin/python main.py
```

The Telethon session (`telethon.session`) is written to the working directory, so run the bot from a writable state directory, not from the code checkout.


# Docker:
```sh
cp config.json.example config.json  # db_uri "mongodb://mongo:27017" for the bundled MongoDB
docker compose --profile mongo up -d --build
docker compose logs -f bot
```

The image carries no secrets: compose bind-mounts only the config file, read-only, at `/etc/spownerbot/config.json`. The source is `./config.json`, or the path in `SPOWNERBOT_CONFIG_FILE`. The bot runs as uid 65532, so the file must be readable by that uid; `cp` leaves it world-readable. A single-file mount keeps the inode it started with, so run `docker compose restart bot` after replacing the file.

The bundled MongoDB is for development and only runs with `--profile mongo`. It publishes no ports and keeps its data in the `spownerbot_mongo-data` volume. The Telethon session lives in the `spownerbot_session` volume.
```sh
docker compose exec mongo mongosh SPOwnerBot                                         # shell
docker compose exec -T mongo mongodump --archive --gzip --db SPOwnerBot > backup.gz   # backup
docker compose exec -T mongo mongorestore --archive --gzip < backup.gz                # restore
```


# Deployment:
Production uses a shared MongoDB on an external Docker network instead of the bundled one. That wiring stays on the host, in a gitignored `compose.override.yaml` next to `docker-compose.yml`, which compose loads automatically:
```yaml
services:
  bot:
    networks:
      - default
      - mongo

networks:
  mongo:
    external: true
    name: <shared MongoDB network>
```

In the config file, point `db_uri` at that network's MongoDB service: `mongodb://<user>:<password>@mongodb:27017/<database>`.

The host renders the config file outside the checkout, for example `/run/secrets/spownerbot/config.json`, owned by uid 65532 with mode 0400. Start the bot with:
```sh
SPOWNERBOT_CONFIG_FILE=/run/secrets/spownerbot/config.json docker compose up -d --build
```

Do not pass `--profile mongo` here. To deploy an update, `git pull` and run the same command again.


# Checks:
```sh
uv run ruff check
uv run ruff format --check
uv run ty check
```

CI (`.github/workflows/ci.yml`) runs the same checks on every push and pull request.
