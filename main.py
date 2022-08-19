from pyrogram import Client, filters, types
from pyrogram.raw.functions.messages import GetStickerSet, GetCustomEmojiDocuments
from pyrogram.raw.types import InputStickerSetShortName
from pyrogram.raw.base.messages import StickerSet
from pyrogram.enums import MessageEntityType

from db import DataBase

from config import API_ID, API_HASH, BOT_TOKEN, DB_URI, DB_NAME, OWNERS, TEXTS

from typing import Callable, List


owners_filter: Callable = lambda client, message: message.from_user.id in OWNERS


db: DataBase = DataBase(
    db_uri = DB_URI,
    db_name = DB_NAME
)


app: Client = Client(
    name = "bot",
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

    set_id: int = response.set.id
    int32_id: int = set_id >> 32

    await message.reply_text(
        text = TEXTS["owner"].format(
            int32_id = int32_id,
            int64_id = 0x100000000 + int32_id
        )
    )


@app.on_message()
async def custom_emojis_handler(client: Client, message: types.Message) -> None:
    if not message.entities:
        return

    for entity in message.entities:
        if entity.type == MessageEntityType.CUSTOM_EMOJI:
            stickers: List[types.Sticker] = await client.get_custom_emoji_stickers(
                custom_emoji_ids = [
                    entity.custom_emoji_id
                ]
            )

            if not stickers:
                return

            sticker: types.Sticker = stickers[0]

            sticker_short_name: str = sticker.set_name

            if not sticker_short_name:
                return

            response: StickerSet = await client.invoke(
                query = GetStickerSet(
                    hash = 0,
                    stickerset = InputStickerSetShortName(
                        short_name = sticker.set_name
                    )
                )
            )

            if not response:
                return

            set_id: int = response.set.id
            int32_id: int = set_id >> 32

            await message.reply_text(
                text = TEXTS["owner"].format(
                    int32_id = int32_id,
                    int64_id = 0x100000000 + int32_id
                )
            )

            return


if __name__ == "__main__":
    app.run()
