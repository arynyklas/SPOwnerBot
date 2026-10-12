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
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp config.py.example config.py  # fill API_ID, API_HASH, BOT_TOKEN, DB_URI
.venv/bin/python main.py
```

Type check: `pip install mypy && mypy .` (strict, see `pyproject.toml`).
