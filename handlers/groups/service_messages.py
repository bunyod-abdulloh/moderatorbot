import asyncio

from aiogram import types
from aiogram.utils.exceptions import MessageCantBeDeleted, BotKicked

from data.config import ADMINS, BOT_ID
from filters.group_chat import IsGroupAdminOrOwner, IsGroupAndBotAdmin
from loader import dp, bot, grpdb, blstdb
from services.error_service import notify_exception_to_admin


@dp.message_handler(IsGroupAndBotAdmin(), content_types=types.ContentType.LEFT_CHAT_MEMBER)
async def banned_member(message: types.Message):
    try:
        await message.delete()
    except BotKicked:
        await bot.send_message(
            chat_id=ADMINS[0],
            text=f"Sizning {(await bot.me).full_name} botingiz {message.chat.full_name} guruhidan chiqarildi!"
        )
        await grpdb.delete_group(group_id=message.chat.id)

    except Exception as err:
        await notify_exception_to_admin(err=err)


# Guruh admini yoki egasi guruhga odam qo'shsa shu handler ushlaydi
@dp.message_handler(IsGroupAdminOrOwner(), content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def new_member_admin(message: types.Message):
    try:
        if not await blstdb.get_group_by_blacklist(message.chat.id):
            await message.answer(
                "Botning faoliyati ushbu guruh uchun cheklangan! Bot adminiga murojaat qiling!"
            )
            await bot.leave_chat(message.chat.id)
            return

        # Foydalanuvchilar ro‘yxati: bosilsa profiliga o‘tadi
        member_names = [
            f'<a href="tg://user?id={m.id}">{m.full_name}</a>'
            for m in message.new_chat_members
            if not m.is_bot
        ]

        # Bot o‘zi qo‘shilganini aniqlash
        is_bot_added = any(m.id == BOT_ID for m in message.new_chat_members)

        if is_bot_added:
            await grpdb.add_group(
                telegram_id=message.from_user.id,
                group_id=message.chat.id
            )
            bot_info = await bot.me
            await bot.send_message(
                chat_id=ADMINS[0],
                text=f"Sizning {bot_info.full_name} botingiz {message.chat.full_name} guruhiga qo'shildi!"
            )
        await message.delete()

        if member_names:
            msg = await message.answer(
                f"Xush kelibsiz: {', '.join(member_names)}!", parse_mode="HTML"
            )
            await asyncio.sleep(5)
            await message.chat.delete_message(msg.message_id)

    except MessageCantBeDeleted:
        await message.answer(
            "Bot guruhga admin qilinmaganligi sababli foydalanuvchi guruhga qo'shilganligi haqidagi xabarni "
            "o'chira olmadi!\n\nBot to'g'ri ishlashi uchun uni admin qiling!"
        )
    except Exception as err:
        await notify_exception_to_admin(err=err)


# Bot guruhda admin bo'lsa yangi qo'shilganlarni tutib oluvchi handler
@dp.message_handler(IsGroupAndBotAdmin(), content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def handle_new_chat_members(message: types.Message):
    try:
        # Foydalanuvchilar ro‘yxati: bosilsa profiliga o‘tadi
        member_names = [
            f'<a href="tg://user?id={m.id}">{m.full_name}</a>'
            for m in message.new_chat_members
            if not m.is_bot
        ]

        # Bot bo‘lsa — chiqazib yuboriladi
        for bot_member in filter(lambda m: m.is_bot, message.new_chat_members):
            await message.chat.kick(user_id=bot_member.id)
            await message.reply(text=f"{message.from_user.full_name} guruhga bot qo'shish mumkin emas!")

        # Foydalanuvchilarga xush kelibsiz xabari
        if member_names:
            msg = await message.answer(
                f"Xush kelibsiz: {', '.join(member_names)}!", parse_mode="HTML"
            )
            await asyncio.sleep(5)
            await message.chat.delete_message(msg.message_id)

    except MessageCantBeDeleted:
        await message.answer(
            "Xabarni o‘chira olmadim, ehtimol bot admin emas. Iltimos, unga admin huquqi bering!"
        )

    except Exception as err:
        await notify_exception_to_admin(err=err)
