from typing import List

from aiogram import types
from filters.group_chat import is_admin, IsGroupAndBotAdmin
from loader import dp, bot

PHONE_REGEX = r"(?<!\d)(\+?\d{1,3}[\s.-]?)?(\(?\d{1,4}\)?[\s.-]?)?\d{1,4}[\s.-]?\d{1,4}[\s.-]?\d{1,9}(?!\d)"
MEDIA_CONTENTS = ['audio', 'video', 'document', 'sticker', 'photo']


async def handle_non_admin_message(message: types.Message):
    if not await is_admin(bot, message.chat.id, message.from_user.id):
        await message.delete()


@dp.message_handler(IsGroupAndBotAdmin(), regexp=PHONE_REGEX)
async def get_phone_numbers(message: types.Message):
    await handle_non_admin_message(message)


@dp.message_handler(IsGroupAndBotAdmin(), is_media_group=True, content_types=['any'])
async def check_media_group(message: types.Message, album: List[types.Message]):
    if not await is_admin(bot, message.chat.id, message.from_user.id):
        for n in album:
            await bot.delete_message(
                chat_id=message.chat.id, message_id=n.message_id
            )


@dp.message_handler(IsGroupAndBotAdmin(), state="*", content_types=['text'])
async def check_the_link(message: types.Message):
    if message.entities:
        await handle_non_admin_message(message)


@dp.message_handler(IsGroupAndBotAdmin(), state="*", content_types=MEDIA_CONTENTS)
async def check_the_media(message: types.Message):
    if message.content_type in MEDIA_CONTENTS:
        await handle_non_admin_message(message)
