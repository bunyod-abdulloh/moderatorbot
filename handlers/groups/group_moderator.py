import re
from typing import List

from aiogram import types
from filters.group_chat import IsGroupAndBotAdmin, IsGroupAdminOrOwner, IsGroupAndForwarded

from loader import dp, bot

PHONE_REGEX = r"(?<!\d)(\+?\d{1,3}[-\s]?)?\(?\d{2,4}\)?[-\s]?\d{2,4}[-\s]?\d{2,4}(?!\d)"
MEDIA_CONTENTS = ['audio', 'video', 'document', 'sticker', 'photo']


async def handle_non_admin_message(message: types.Message):
    if await IsGroupAdminOrOwner().check(message):
        return

    if await IsGroupAndForwarded().check(message):
        return

    # Xabarni o'chirish
    await message.delete()


@dp.message_handler(IsGroupAndBotAdmin(), IsGroupAndForwarded(), regexp=PHONE_REGEX, content_types=types.ContentTypes.ANY)
async def get_forward_phone_numbers(message: types.Message):
    if await IsGroupAdminOrOwner().check(message):
        return

    # Forward qilingan chat boshqa chatdan bo‘lsa, o‘chirish
    if message.forward_from_chat and message.forward_from_chat.id != message.chat.id:
        await message.delete()
        return

    # Forward qilingan foydalanuvchi ismi mavjud bo‘lsa, o‘chirish
    if message.forward_sender_name:
        await message.delete()
        return

    # Forward qilingan foydalanuvchi admin yoki creator bo‘lmasa, o‘chirish
    if message.forward_from:
        member = await message.chat.get_member(message.forward_from.id)
        if member.status not in ['administrator', 'creator']:
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
