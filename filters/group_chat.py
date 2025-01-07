from aiogram import types, Bot
from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import ChatMemberStatus


class IsGroup(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        return message.chat.type in (
            types.ChatType.GROUP,
            types.ChatType.SUPERGROUP,
        )


class IsGroupPhoto(BoundFilter):
    """Guruh va rasmli xabarlarni tekshirish uchun yagona filtr."""

    async def check(self, message: types.Message) -> bool:
        # Guruh yoki superguruhda ekanligini tekshirish
        if message.chat.type not in (types.ChatType.GROUP, types.ChatType.SUPERGROUP):
            return False
        # Xabarda rasm borligini tekshirish
        return bool(message.photo)


class IsGroupAdminOrOwner(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        # Guruhda bo'lishi va foydalanuvchining statusini tekshirish
        if message.chat.type not in [types.ChatType.GROUP, types.ChatType.SUPERGROUP]:
            return False

        # `get_chat_member` metodidan foydalangan holda foydalanuvchining statusini tekshirish
        member = await message.chat.get_member(message.from_user.id)

        return member.status in [types.ChatMemberStatus.ADMINISTRATOR, types.ChatMemberStatus.CREATOR]


async def is_admin(bot: Bot, chat_id: int, user_id: int) -> bool:
    """Foydalanuvchi guruh administratori ekanligini tekshirish."""
    member = await bot.get_chat_member(chat_id, user_id)
    return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]
