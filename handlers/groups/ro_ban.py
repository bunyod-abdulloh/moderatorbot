import asyncio
import datetime
import re

from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.utils.exceptions import BadRequest

from filters import IsGroupAndBotAdmin
from loader import dp
from services.error_service import notify_exception_to_admin


@dp.message_handler(IsGroupAndBotAdmin(), Command("ro", prefixes="!/"), is_admin=True)
async def read_only_mode(message: types.Message):
    try:
        member = message.reply_to_message.from_user
        member_id = member.id

        command_parse = re.match(r"(!ro|/ro) ?(\d+)? ?([\w+\D]+)?", message.text)
        time = int(command_parse.group(2) or 5)
        comment = command_parse.group(3)

        until_date = datetime.datetime.now() + datetime.timedelta(minutes=time)

        await message.chat.restrict(user_id=member_id, can_send_messages=False, until_date=until_date)
        await message.reply_to_message.delete()

        msg = f"Foydalanuvchi {member.full_name} {time} daqiqa yozish huquqidan mahrum qilindi!"
        if comment:
            msg += f"\nSabab:\n<b>{comment}</b>\n"
        await message.answer(text=msg)

        service_message = await message.reply("Xabar 5 soniyadan so'ng o'chib ketadi.")
        await asyncio.sleep(5)
        await message.delete()
        await service_message.delete()
    except BadRequest as err:
        await message.answer(f"Xatolik: {err}")

    except Exception as err:
        await notify_exception_to_admin(err=err)


# Undo read-only mode
@dp.message_handler(Command("unro", prefixes="!/"))
async def undo_read_only_mode(message: types.Message):
    member = message.reply_to_message.from_user
    member_id = member.id

    user_allowed = types.ChatPermissions(can_send_messages=True, can_send_media_messages=True,
                                         can_send_polls=True, can_send_other_messages=True,
                                         can_add_web_page_previews=True, can_invite_users=True)
    await message.chat.restrict(user_id=member_id, permissions=user_allowed, until_date=0)
    await message.answer(f"Foydalanuvchi {member.full_name} tiklandi.")

    service_message = await message.reply("Xabar 5 soniyadan so'ng o'chib ketadi.")
    await asyncio.sleep(5)
    await message.delete()
    await service_message.delete()


# Ban user
# @dp.message_handler(IsGroupAndBotAdmin(), Command("ban", prefixes="!/"), AdminFilter())
# async def ban_user(message: types.Message):
#     member = message.reply_to_message.from_user
#     member_id = member.id
#
#     await message.chat.kick(user_id=member_id)
#     await message.answer(f"Foydalanuvchi {member.full_name} guruhdan haydaldi.")
#
#     service_message = await message.reply("Xabar 5 soniyadan so'ng o'chib ketadi.")
#     await asyncio.sleep(5)
#     await message.delete()
#     await service_message.delete()
#
#
# # Unban user
# @dp.message_handler(IsGroupAndBotAdmin(), Command("unban", prefixes="!/"), AdminFilter())
# async def unban_user(message: types.Message):
#     member = message.reply_to_message.from_user
#     member_id = member.id
#
#     await message.chat.unban(user_id=member_id)
#     await message.answer(f"Foydalanuvchi {member.full_name} bandan chiqarildi.")
#
#     service_message = await message.reply("Xabar 5 soniyadan so'ng o'chib ketadi.")
#     await asyncio.sleep(5)
#     await message.delete()
#     await service_message.delete()
