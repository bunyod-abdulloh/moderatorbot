import asyncio

import aiogram
from aiogram import types

from loader import bot, udb
from services.error_service import notify_exception_to_admin


async def send_message_to_users(message: types.Message):
    all_users = await udb.select_all_users()
    success_count, failed_count = 0, 0

    for index, user in enumerate(all_users, start=1):
        try:
            await message.copy_to(chat_id=user["telegram_id"])
            success_count += 1
        except aiogram.exceptions.BotBlocked:
            failed_count += 1
            await udb.delete_user(user["telegram_id"])
        except Exception as err:
            await notify_exception_to_admin(err=err)
        if index % 1500 == 0:
            await asyncio.sleep(30)
        await asyncio.sleep(0.05)

    return success_count, failed_count


async def send_media_group_to_users(media_group: types.MediaGroup):
    all_users = await udb.select_all_users()
    success_count, failed_count = 0, 0

    for index, user in enumerate(all_users, start=1):
        try:
            await bot.send_media_group(chat_id=user['telegram_id'], media=media_group)
            success_count += 1
        except aiogram.exceptions.BotBlocked:
            failed_count += 1
            await udb.delete_user(user["telegram_id"])
        except Exception as err:
            await notify_exception_to_admin(err=err)
        if index % 1500 == 0:
            await asyncio.sleep(30)
        await asyncio.sleep(0.05)

    return success_count, failed_count
