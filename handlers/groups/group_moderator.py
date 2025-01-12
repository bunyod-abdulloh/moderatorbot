from aiogram import types
from filters.group_chat import is_admin, IsGroupAndBotAdmin
from loader import dp, bot

PHONE_REGEX = r"(?<!\d)(\+?\d{1,3}[\s.-]?)?(\(?\d{1,4}\)?[\s.-]?)?\d{1,4}[\s.-]?\d{1,4}[\s.-]?\d{1,9}(?!\d)"
DELETE_LINK_CONTENTS = ['audio', 'video', 'document', 'text']
DELETE_MEDIA_CONTENTS = ['audio', 'video', 'document', 'sticker']


async def handle_non_admin_message(message: types.Message):
    """
    Foydalanuvchi admin bo'lmasa, xabarni o'chiradi.
    """
    if not await is_admin(bot, message.chat.id, message.from_user.id):
        await message.delete()


@dp.message_handler(IsGroupAndBotAdmin(), regexp=PHONE_REGEX)
async def get_phone_numbers(message: types.Message):
    """
    Telefon raqamlarini o'z ichiga olgan xabarlar uchun tekshiruv.
    """
    await handle_non_admin_message(message)


@dp.message_handler(IsGroupAndBotAdmin(), state="*", is_media_group=True)
async def check_media_group(message: types.Message):
    """
    Media-guruh ichidagi xabarlarni tekshiradi.
    """
    if message.entities or message.caption_entities:
        await handle_non_admin_message(message)


@dp.message_handler(IsGroupAndBotAdmin(), state="*", content_types=DELETE_LINK_CONTENTS)
async def check_the_link(message: types.Message):
    """
    Xabardagi havolalarni tekshiradi.
    """
    if message.entities or message.caption_entities:
        await handle_non_admin_message(message)


@dp.message_handler(IsGroupAndBotAdmin(), state="*", content_types=DELETE_MEDIA_CONTENTS)
async def check_the_media(message: types.Message):
    """
    Xabardagi medialarni tekshiradi.
    """
    if message.content_type in DELETE_MEDIA_CONTENTS:
        await handle_non_admin_message(message)
