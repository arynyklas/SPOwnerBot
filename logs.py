"""JSON logging: one object per line on stdout."""

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any, Final, override

# Attributes every LogRecord carries; anything else came in through `extra=`.
# "message" and "asctime" are added by Formatter.format().
_RECORD_ATTRS: Final[frozenset[str]] = frozenset(
    vars(logging.LogRecord("", logging.NOTSET, "", 0, "", None, None))
) | {"message", "asctime"}


class JSONFormatter(logging.Formatter):
    @override
    def format(self, record: logging.LogRecord) -> str:
        entry: dict[str, Any] = {
            "ts": datetime.fromtimestamp(record.created, UTC)
            .isoformat(timespec="milliseconds")
            .replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }

        if record.exc_info:
            entry["exc"] = self.formatException(record.exc_info)

        for key, value in vars(record).items():
            if key not in _RECORD_ATTRS:
                # An extra can't shadow the fixed keys above
                entry.setdefault(key, value)

        return json.dumps(entry, default=str)


def setup_logging(level: int = logging.INFO) -> None:
    """Routes the root logger, and so Telethon's and PyMongo's, to JSON stdout."""
    handler: logging.StreamHandler[Any] = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    logging.basicConfig(level=level, handlers=[handler], force=True)
