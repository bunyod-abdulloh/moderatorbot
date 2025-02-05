from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from loader import bot

chat_types = ['group', 'supergroup']


class IsGroupAdminOrOwner(BoundFilter):

    async def check(self, message: types.Message) -> bool:
        member = await message.chat.get_member(message.from_user.id)
        return member.is_chat_admin() or member.is_chat_creator()


class IsGroupAndBotAdmin(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        if message.chat.type not in chat_types:
            return False

        # Botning admin ekanligini tekshirish
        bot_id = (await bot.me).id
        chat_member = await bot.get_chat_member(message.chat.id, bot_id)
        return chat_member.is_chat_creator() or chat_member.is_chat_admin()


class IsGroupAdminAndForwarded(BoundFilter):
    """Guruhda bot admin ekanligini va xabar forward qilinganligini tekshiruvchi filter."""

    async def check(self, message: types.Message) -> bool:

        # Guruh ekanligini tekshirish
        if message.chat.type not in chat_types:
            return False

        # Botning admin ekanligini tekshirish
        bot_id = (await bot.me).id
        chat_member = await bot.get_chat_member(message.chat.id, bot_id)
        if not (chat_member.is_chat_creator() or chat_member.is_chat_admin()):
            return False

        # Xabar forward qilinganligini tekshirish
        return bool(message.forward_from_chat or message.forward_from or message.forward_sender_name)
