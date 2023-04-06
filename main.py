from pyrogram import Client, filters, types
from pyrogram.raw.types.messages.sticker_set import StickerSet
from pyrogram.raw.functions.messages import GetStickerSet
from pyrogram.raw.types import InputStickerSetShortName
from pyrogram.enums import MessageEntityType
from db import DataBase

from basic_data import TEXTS
from config import API_ID, API_HASH, BOT_TOKEN, DB_URI, DB_NAME

from typing import List, Union


db: DataBase = DataBase(
    db_uri = DB_URI,
    db_name = DB_NAME
)


app: Client = Client(
    name = DB_NAME,
    api_id = API_ID,
    api_hash = API_HASH,
    bot_token = BOT_TOKEN
)


@app.on_message(filters.command(["start"]) & filters.private)
async def start_command_handler(client: Client, message: types.Message) -> None:
    if not db.get_user(
        user_id = message.from_user.id
    ):
        db.add_user(
            user_id = message.from_user.id
        )

    await message.reply_text(
        text = TEXTS["start"]
    )


async def send_owner_message(message: types.Message, set_id: int) -> None:
    user_id: int = set_id >> 32

    set_increment_id: Union[int, None] = None

    if set_id >> 24 & 0xff:
        user_id = user_id + 0x100000000
    else:
        set_increment_id = set_id & 0xffffffff

    await message.reply_text(
        text = TEXTS["owner"].format(
            user_id = user_id,
            set_increment_id = set_increment_id
        )
    )


@app.on_message(filters.sticker)
async def stickers_handler(client: Client, message: types.Message) -> None:
    sticker_short_name: str = message.sticker.set_name

    if not sticker_short_name:
        return

    response: StickerSet = await client.invoke(
        query = GetStickerSet(
            hash = 0,
            stickerset = InputStickerSetShortName(
                short_name = sticker_short_name
            )
        )
    )

    if not response:
        return

    await send_owner_message(
        message = message,
        set_id = response.set.id
    )


@app.on_message()
async def custom_emojis_handler(client: Client, message: types.Message) -> None:
    if not message.entities:
        return

    custom_emoji_ids: List[int] = []

    for entity in message.entities:
        entity: types.MessageEntity

        if entity.type != MessageEntityType.CUSTOM_EMOJI:
            continue

        custom_emoji_ids.append(entity.custom_emoji_id)

        if len(custom_emoji_ids) == 50:
            break

    stickers: List[types.Sticker] = await client.get_custom_emoji_stickers(
        custom_emoji_ids = custom_emoji_ids
    )

    if not stickers:
        return

    parsed_sticker_sets: List[str] = []

    for sticker in stickers:
        sticker: types.Sticker

        sticker_short_name: str = sticker.set_name

        if not sticker_short_name or sticker_short_name in parsed_sticker_sets:
            continue

        parsed_sticker_sets.append(sticker_short_name)

        response: StickerSet = await client.invoke(
            query = GetStickerSet(
                stickerset = InputStickerSetShortName(
                    short_name = sticker_short_name
                ),
                hash = 0
            )
        )

        if not response:
            continue

        await send_owner_message(
            message = message,
            set_id = response.set.id
        )


if __name__ == "__main__":
    app.run()
