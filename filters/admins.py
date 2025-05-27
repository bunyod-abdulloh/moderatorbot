from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from data.config import ADMINS


class AdminFilter(BoundFilter):
    key = 'is_admin'

    def __init__(self, is_admin):
        self.is_admin = is_admin

    async def check(self, message: types.Message) -> bool:
        member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
        return member.status in ("administrator", "creator")


class IsBotAdminFilter(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        admin_ids_int = [int(id) for id in ADMINS]
        return int(message.from_user.id) in admin_ids_int
