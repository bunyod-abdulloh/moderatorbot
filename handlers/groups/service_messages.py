import asyncio

from aiogram import types
from aiogram.utils.exceptions import MessageCantBeDeleted, BotKicked

from data.config import ADMINS, BOT_ID
from filters.group_chat import IsGroupAdminOrOwner, IsGroupAndBotAdmin
from loader import dp, bot, db
from services.error_service import notify_exception_to_admin


def get_restrict_permissions(can_send: bool):
    return types.ChatPermissions(
        can_send_messages=can_send,
        can_send_media_messages=can_send,
        can_send_other_messages=can_send,
        can_invite_users=True
    )


async def restrict_message(message: types.Message, member_names: list, group: list):
    msg = await message.answer(
        text=f"Xush kelibsiz, {', '.join(member_names)}!\n\nGuruhda yozish uchun {group['users']} ta "
             f"foydalanuvchi qo'shishingiz lozim!")
    return msg


@dp.message_handler(IsGroupAndBotAdmin(), content_types=types.ContentType.LEFT_CHAT_MEMBER)
async def banned_member(message: types.Message):
    try:
        await message.delete()

    except BotKicked:
        await bot.send_message(
            chat_id=ADMINS[0],
            text=f"Sizning {(await bot.me).full_name} botingiz {message.chat.full_name} guruhidan chiqarildi!"
        )
        await db.delete_group(group_id=message.chat.id)

    except Exception as err:
        await notify_exception_to_admin(err=err)


# Guruh admini yoki egasi guruhga odam qo'shsa shu handler ushlaydi
@dp.message_handler(IsGroupAdminOrOwner(), content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def new_member_admin(message: types.Message):
    try:
        # Qora ro'yxat tekshiruvi
        check_blacklist = await db.get_group_by_blacklist(message.chat.id)

        if not check_blacklist:
            await message.answer("Botning faoliyati ushbu guruh uchun cheklangan! Bot adminiga murojaat qiling!")
            await bot.leave_chat(message.chat.id)
            return

        member_names = []
        add_bot = False
        for member in message.new_chat_members:
            # Xush kelibsizlar uchun ism yig‘iladi
            member_names.append(member.full_name)

            # Agar botning o‘zi qo‘shilgan bo‘lsa
            if member.id == BOT_ID:
                add_bot = True

        if add_bot:
            await db.add_group(telegram_id=message.from_user.id, group_id=message.chat.id)
            await bot.send_message(
                chat_id=ADMINS[0],
                text=f"Sizning {(await bot.me).full_name} botingiz {message.chat.full_name} guruhiga qo'shildi!"
            )

        # Xabar yuborish va o'chirish
        if member_names:
            msg = await message.answer(
                f"Xush kelibsiz: {', '.join(member_names)}!", parse_mode="HTML"
            )
            await asyncio.sleep(5)
            await message.chat.delete_message(msg.message_id)

    except MessageCantBeDeleted:
        await message.answer(
            text="Bot guruhga admin qilinmaganligi sababli foydalanuvchi guruhga qo'shilganligi haqidagi xabarni "
                 "o'chirmadi!\n\nBot to'g'ri ishlashi uchun botni guruhga admin qilishingiz lozim!"
        )

    except Exception as err:
        await notify_exception_to_admin(err=err)


# Bot guruhda bo'lsa va admin bo'lsa yangi qo'shilgan odamlarni ushlaydigan handler
@dp.message_handler(IsGroupAndBotAdmin(), content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def handle_new_chat_members(message: types.Message):
    try:
        member_names = []

        for member in message.new_chat_members:
            if member.is_bot:
                await message.chat.kick(user_id=member.id)
            else:
                member_names.append(member.full_name)

        if member_names:
            msg = await message.answer(
                f"Xush kelibsiz: {', '.join(member_names)}!", parse_mode="HTML"
            )
            await asyncio.sleep(5)
            await message.chat.delete_message(msg.message_id)

    except Exception as err:
        await notify_exception_to_admin(err=err)
