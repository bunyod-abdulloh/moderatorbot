import re
from typing import List

from aiogram import types
from filters.group_chat import IsGroupAndBotAdmin, IsGroupAndForwardedFromAnotherChat, IsGroupAdminOrOwner

from loader import dp, bot

PHONE_REGEX = r"(?<!\d)(\+?\d{1,3}[-\s]?)?\(?\d{2,4}\)?[-\s]?\d{2,4}[-\s]?\d{2,4}(?!\d)"
MEDIA_CONTENTS = ['audio', 'video', 'document', 'sticker', 'photo']


async def handle_non_admin_message(message: types.Message):
    if await IsGroupAdminOrOwner().check(message):
        return

    if await IsGroupAndForwardedFromAnotherChat().check(message):
        return

    # Xabarni o'chirish
    await message.delete()


@dp.message_handler(IsGroupAndBotAdmin(), regexp=PHONE_REGEX, content_types=types.ContentTypes.ANY)
async def get_phone_numbers(message: types.Message):
    if await IsGroupAdminOrOwner().check(message):
        return
    else:
        if message.forward_from_chat:
            # Regex `regexp` orqali tekshirildi, endi natijani qaytaramiz
            if message.caption:
                match = re.search(PHONE_REGEX, message.caption)
            else:
                match = re.search(PHONE_REGEX, message.text)

            if match:
                await message.delete()


@dp.message_handler(IsGroupAndBotAdmin(), is_media_group=True, content_types=types.ContentTypes.ANY)
async def check_media_group(message: types.Message, album: List[types.Message]):
    if await IsGroupAdminOrOwner().check(message):
        return

    if message.forward_from_chat:
        for n in album:
            await bot.delete_message(
                chat_id=message.chat.id, message_id=n.message_id
            )


@dp.message_handler(IsGroupAndBotAdmin(), content_types=types.ContentTypes.ANY)
async def handle_forwarded_photos(message: types.Message):
    if await IsGroupAdminOrOwner().check(message):
        return

    if message.forward_from_chat:
        await handle_non_admin_message(message)


@dp.message_handler(IsGroupAndBotAdmin(), state="*", content_types=types.ContentTypes.ANY)
async def check_the_link(message: types.Message):
    if await IsGroupAdminOrOwner().check(message):
        return

    if message.forward_from_chat and message.entities:
        await handle_non_admin_message(message)
