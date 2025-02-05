from aiogram import types
from filters.group_chat import IsGroupAdminAndForwarded, IsGroupAndBotAdmin, IsGroupAndForwarded, IsGroupAdminOrOwner
from loader import dp
import re

PHONE_REGEX = re.compile(r"(?<!\d)(\+?\d{1,3}[-\s]?)?\(?\d{2,4}\)?[-\s]?\d{2,4}[-\s]?\d{2,4}(?!\d)")


async def should_delete_message(message: types.Message) -> bool:
    """Forward qilingan xabarni o‘chirish kerakligini aniqlaydi."""
    if message.forward_from_chat and message.forward_from_chat.id != message.chat.id:
        return True
    if message.forward_sender_name:
        return True
    if message.forward_from:
        return (await message.chat.get_member(message.forward_from.id)).status not in ['administrator', 'creator']
    return False


@dp.message_handler(IsGroupAdminAndForwarded(), content_types=[types.ContentTypes.CONTACT, types.ContentTypes.ANY])
@dp.message_handler(IsGroupAdminAndForwarded(), regexp=PHONE_REGEX, content_types=types.ContentTypes.ANY)
async def get_forward_phone_numbers(message: types.Message):
    if await IsGroupAdminOrOwner().check(message):
        return
    if await should_delete_message(message):
        await message.delete()


@dp.message_handler(IsGroupAndBotAdmin(), content_types=[types.ContentTypes.CONTACT, types.ContentTypes.ANY])
@dp.message_handler(IsGroupAndBotAdmin(), regexp=PHONE_REGEX, content_types=types.ContentTypes.ANY)
async def handle_contact_message(message: types.Message):
    if await IsGroupAdminOrOwner().check(message):
        return
    await message.delete()


@dp.message_handler(IsGroupAndForwarded(), content_types=types.ContentTypes.ANY, is_media_group=True)
@dp.message_handler(IsGroupAndForwarded(), content_types=types.ContentTypes.ANY)
async def handle_forwarded_messages(message: types.Message):
    if await IsGroupAdminOrOwner().check(message):
        return
    if await should_delete_message(message):
        await message.delete()


@dp.message_handler(IsGroupAndBotAdmin(), content_types=types.ContentTypes.ANY, is_media_group=True)
@dp.message_handler(IsGroupAndBotAdmin(), content_types=types.ContentTypes.ANY)
async def handle_oddiy_messages(message: types.Message):
    if await IsGroupAdminOrOwner().check(message):
        return
    if message.caption_entities or message.entities:
        await message.delete()
