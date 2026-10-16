import logging
from typing import Final, cast

from pymongo.errors import PyMongoError
from telethon import TelegramClient, events
from telethon.tl.custom import Message
from telethon.tl.functions.messages import GetCustomEmojiDocumentsRequest
from telethon.tl.types import (
    Document,
    DocumentAttributeCustomEmoji,
    DocumentAttributeSticker,
    InputStickerSetID,
    MessageEntityCustomEmoji,
    TypeDocument,
)

from basic_data import TEXTS
from config import API_HASH, API_ID, BOT_TOKEN, DB_NAME, DB_URI
from db import DataBase
from logs import setup_logging

MAX_CUSTOM_EMOJIS: Final[int] = 50


logger: logging.Logger = logging.getLogger(__name__)


db: DataBase = DataBase(db_uri=DB_URI, db_name=DB_NAME)


client: TelegramClient = TelegramClient(
    session="telethon", api_id=API_ID, api_hash=API_HASH
)

client.parse_mode = "html"


def decode_set_id(set_id: int) -> tuple[int, int]:
    """Returns `(owner user ID, owner's set increment ID)`."""

    # set id = (owner & 0x7FFFFFFF) << 32 | ~((owner >> 31) << 22 | set_increment_id)
    #
    # The high word carries only the low 31 bits of the owner's id; the complement of
    # the low word splits into a 10-bit band (owner >> 31) and a 22-bit per-owner set
    # counter. Reading the band arithmetically replaces the markers this used to match
    # (0xFF3FFFFF is the first set of band 3, a non-zero top byte was taken to mean
    # band 2), each of which covered one band and missed by a multiple of 2^31 as soon
    # as user ids reached the next one. Band 5 needs no further change.
    #
    # A set whose owner's id fit in 31 bits predates the band field: its low word is a
    # plain small counter, so its top byte is zero. A modern id cannot look like that -
    # bands 0-3 put 0xFF in that byte, bands 4-7 0xFE, and it reaches zero only at
    # band 1020.
    high_word: int = set_id >> 32
    low_word: int = set_id & 0xFFFFFFFF

    if low_word >> 24 == 0:
        return high_word, low_word

    return high_word + (((~low_word & 0xFFFFFFFF) >> 22) << 31), ~low_word & 0x3FFFFF


def get_set_id(document: TypeDocument | None) -> int | None:
    """Set ID carried by the sticker document itself; no GetStickerSet round trip."""

    if not isinstance(document, Document):
        return None

    for attribute in document.attributes:
        if isinstance(
            attribute, (DocumentAttributeSticker, DocumentAttributeCustomEmoji)
        ) and isinstance(attribute.stickerset, InputStickerSetID):
            return attribute.stickerset.id

    return None


async def reply_owner(message: Message, set_id: int) -> None:
    user_id, set_increment_id = decode_set_id(set_id)

    await message.reply(
        message=TEXTS.owner.format(user_id=user_id, set_increment_id=set_increment_id)
    )


async def start_command_handler(event: events.NewMessage.Event) -> None:
    message: Message = cast(Message, event.message)
    user_id: int | None = cast(int | None, message.sender_id)

    if user_id is not None:
        await db.add_user(user_id=user_id)

    await message.respond(message=TEXTS.start)


async def sticker_handler(event: events.NewMessage.Event) -> None:
    message: Message = cast(Message, event.message)
    set_id: int | None = get_set_id(message.sticker)

    if set_id is None:
        return

    await reply_owner(message=message, set_id=set_id)


async def custom_emojis_handler(event: events.NewMessage.Event) -> None:
    message: Message = cast(Message, event.message)

    custom_emoji_ids: list[int] = list(
        dict.fromkeys(
            entity.document_id
            for entity in message.entities or []
            if isinstance(entity, MessageEntityCustomEmoji)
        )
    )[:MAX_CUSTOM_EMOJIS]

    if not custom_emoji_ids:
        return

    documents: list[TypeDocument] = cast(
        list[TypeDocument],
        await client(GetCustomEmojiDocumentsRequest(document_id=custom_emoji_ids)),
    )

    replied_set_ids: set[int] = set()

    for document in documents:
        set_id: int | None = get_set_id(document)

        if set_id is None or set_id in replied_set_ids:
            continue

        replied_set_ids.add(set_id)

        await reply_owner(message=message, set_id=set_id)


def main() -> None:
    setup_logging()

    client.add_event_handler(
        start_command_handler,
        events.NewMessage(
            incoming=True, pattern=r"(?i)^/start\b", func=lambda event: event.is_private
        ),
    )

    client.add_event_handler(sticker_handler, events.NewMessage(incoming=True))

    client.add_event_handler(custom_emojis_handler, events.NewMessage(incoming=True))

    try:
        client.loop.run_until_complete(db.create_indexes())
    except PyMongoError:
        # Sticker lookups don't need MongoDB, so a DB outage must not block startup
        logger.exception("Can't create MongoDB indexes")

    client.start(bot_token=BOT_TOKEN)

    client.run_until_disconnected()


if __name__ == "__main__":
    main()
