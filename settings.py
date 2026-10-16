"""Bot settings, read once at start-up from a JSON file.

The file holds the secrets, so errors name the file and the keys but never
echo a value.
"""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

CONFIG_PATH_ENV: Final[str] = "SPOWNERBOT_CONFIG"
DEFAULT_CONFIG_PATH: Final[Path] = Path("/etc/spownerbot/config.json")


class ConfigError(Exception):
    """The config file is missing, unreadable or malformed."""


@dataclass(frozen=True, slots=True)
class Config:
    api_id: int
    api_hash: str
    bot_token: str
    db_uri: str
    db_name: str


# `type(value) is kind`, not isinstance(): JSON true/false must not pass as int
_KEY_TYPES: Final[dict[str, type]] = {
    "api_id": int,
    "api_hash": str,
    "bot_token": str,
    "db_uri": str,
    "db_name": str,
}

_TYPE_NAMES: Final[dict[type, str]] = {int: "an integer", str: "a non-empty string"}


def config_path() -> Path:
    """`$SPOWNERBOT_CONFIG` if set and non-empty, else the default path."""
    return Path(os.environ.get(CONFIG_PATH_ENV) or DEFAULT_CONFIG_PATH)


def _problems(data: dict[str, Any]) -> list[str]:
    problems: list[str] = []

    for key, kind in _KEY_TYPES.items():
        if key not in data:
            problems.append(f"missing key {key!r}")
            continue

        value: Any = data[key]

        if type(value) is not kind or (kind is str and not value.strip()):
            problems.append(f"{key!r} must be {_TYPE_NAMES[kind]}")

    return problems


def load_config(path: Path | None = None) -> Config:
    """Reads and validates the config file; raises `ConfigError` if unusable."""
    if path is None:
        path = config_path()

    try:
        with path.open(encoding="utf-8") as file:
            data: Any = json.load(file)
    except OSError as error:
        raise ConfigError(
            f"can't read config file {path}: {error.strerror or type(error).__name__}"
        ) from None
    except json.JSONDecodeError as error:
        # error.msg is the parser's complaint ("Expecting value"), not the text
        raise ConfigError(
            f"config file {path} is not valid JSON: {error.msg}"
            f" (line {error.lineno}, column {error.colno})"
        ) from None
    except UnicodeDecodeError:
        raise ConfigError(f"config file {path} is not valid UTF-8") from None

    if not isinstance(data, dict):
        raise ConfigError(f"config file {path} must hold a JSON object")

    problems: list[str] = _problems(data)

    if problems:
        raise ConfigError(f"invalid config file {path}: {'; '.join(problems)}")

    return Config(
        api_id=data["api_id"],
        api_hash=data["api_hash"],
        bot_token=data["bot_token"],
        db_uri=data["db_uri"],
        db_name=data["db_name"],
    )
