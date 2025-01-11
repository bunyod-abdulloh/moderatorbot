import asyncio
import datetime
import re

from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.utils.exceptions import BadRequest

from filters import IsGroup, AdminFilter
from loader import dp, bot, db

PHONE_REGEX = r"(?<!\d)(\+?\d{1,3}[\s.-]?)?(\(?\d{1,4}\)?[\s.-]?)?\d{1,4}[\s.-]?\d{1,4}[\s.-]?\d{1,9}(?!\d)"


@dp.message_handler(IsGroup(), regexp=PHONE_REGEX)
async def get_phone_numbers(message: types.Message):
    admin_or_owner = ['administrator', 'creator']
    status = (await bot.get_chat_member(message.chat.id, message.from_user.id)).status

    if status in admin_or_owner:
        pass
    else:
        await message.reply("Iltimos, telefon raqamlarini xabarda yubormang!")
        await message.delete()


# Read-only mode handler
@dp.message_handler(IsGroup(), Command("ro", prefixes="!/"), AdminFilter())
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

        msg = f"Foydalanuvchi {member.full_name} {time} minut yozish huquqidan mahrum qilindi."
        if comment:
            msg += f"\nSabab:\n<b>{comment}</b>"
        await message.answer(text=msg)

        service_message = await message.reply("Xabar 5 sekunddan so'ng o'chib ketadi.")
        await asyncio.sleep(5)
        await message.delete()
        await service_message.delete()
    except BadRequest as err:
        await message.answer(f"Xatolik: {err}")


# Undo read-only mode
@dp.message_handler(IsGroup(), Command("unro", prefixes="!/"), AdminFilter())
async def undo_read_only_mode(message: types.Message):
    member = message.reply_to_message.from_user
    member_id = member.id

    user_allowed = types.ChatPermissions(can_send_messages=True, can_send_media_messages=True,
                                         can_send_polls=True, can_send_other_messages=True,
                                         can_add_web_page_previews=True, can_invite_users=True)
    await message.chat.restrict(user_id=member_id, permissions=user_allowed, until_date=0)
    await message.answer(f"Foydalanuvchi {member.full_name} tiklandi.")

    service_message = await message.reply("Xabar 5 sekunddan so'ng o'chib ketadi.")
    await asyncio.sleep(5)
    await message.delete()
    await service_message.delete()


# Ban user
@dp.message_handler(IsGroup(), Command("ban", prefixes="!/"), AdminFilter())
async def ban_user(message: types.Message):
    member = message.reply_to_message.from_user
    member_id = member.id

    await message.chat.kick(user_id=member_id)
    await message.answer(f"Foydalanuvchi {member.full_name} guruhdan haydaldi.")

    service_message = await message.reply("Xabar 5 sekunddan so'ng o'chib ketadi.")
    await asyncio.sleep(5)
    await message.delete()
    await service_message.delete()


# Unban user
@dp.message_handler(IsGroup(), Command("unban", prefixes="!/"), AdminFilter())
async def unban_user(message: types.Message):
    member = message.reply_to_message.from_user
    member_id = member.id

    await message.chat.unban(user_id=member_id)
    await message.answer(f"Foydalanuvchi {member.full_name} bandan chiqarildi.")

    service_message = await message.reply("Xabar 5 sekunddan so'ng o'chib ketadi.")
    await asyncio.sleep(5)
    await message.delete()
    await service_message.delete()


# Check media group messages
@dp.message_handler(IsGroup(), state="*", content_types="any", is_media_group=True)
async def check_media_group(message: types.Message):
    try:
        group = await db.get_group(group_id=message.chat.id)
        if group and not (await bot.get_chat_member(chat_id=group, user_id=message.from_user.id)).status in ['creator',
                                                                                                             'administrator',
                                                                                                             'owner']:
            if message.entities or message.caption_entities:
                await message.delete()
                await message.answer(f"{message.from_user.full_name}, iltimos, reklama tarqatmang!")
    except Exception:
        pass


# Check links in messages
@dp.message_handler(IsGroup(), state="*", content_types=['text', 'video', 'photo'])
async def check_the_link(message: types.Message):
    try:
        group = await db.get_group(group_id=message.chat.id)
        if group and not (await bot.get_chat_member(chat_id=group, user_id=message.from_user.id)).status in ['creator',
                                                                                                             'administrator',
                                                                                                             'owner']:
            if message.entities or message.caption_entities:
                await message.delete()
                await message.answer(f"{message.from_user.full_name}, iltimos, reklama tarqatmang!")

            # if re.search(PHONE_REGEX, message.text):
            #     await message.reply("Iltimos, telefon raqamlarini xabarda yubormang!")
    except Exception:
        pass
