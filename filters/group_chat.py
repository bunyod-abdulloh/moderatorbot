from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from aiogram.utils.exceptions import BotKicked, BadRequest

from data.config import ADMINS
from loader import db, bot

chat_types = ['group', 'supergroup']


class IsGroup(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        return message.chat.type in chat_types


class IsGroupPhoto(BoundFilter):
    """Guruh va rasmli xabarlarni tekshirish uchun yagona filtr."""

    async def check(self, message: types.Message) -> bool:
        # Guruh yoki superguruhda ekanligini tekshirish
        if message.chat.type not in chat_types:
            return False
        # Xabarda rasm borligini tekshirish
        return bool(message.photo)


class IsGroupAdminOrOwner(BoundFilter):

    async def check(self, message: types.Message) -> bool:
        member = await message.chat.get_member(message.from_user.id)
        return member.is_chat_admin() or member.is_chat_creator()


class IsGroupAndBotAdmin(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        bot_info = await bot.me

        if message.chat.type not in chat_types:
            return False

        # Botning admin ekanligini tekshirish
        chat_member = await bot.get_chat_member(message.chat.id, bot_info.id)
        return chat_member.is_chat_creator() or chat_member.is_chat_admin()


class IsGroupAndForwarded(BoundFilter):
    """Guruhda forward qilingan xabarlarni aniqlash."""

    async def check(self, message: types.Message) -> bool:
        # Xabar forward qilingan bo‘lsa, true qaytarish
        if message.forward_from_chat or message.forward_from or message.forward_sender_name:
            return True

        return False
