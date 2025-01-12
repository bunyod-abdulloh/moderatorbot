import asyncio
from typing import List

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import BotKicked
from magic_filter import F

from keyboards.inline.admin_ibuttons import button_generator
from loader import dp, db, bot


async def send_to_groups(message: types.Message, groups: List[dict], media_group=None):
    """
    Guruhlarga xabar yoki media-guruh yuborish.
    """
    success_count, failed_count = 0, 0
    for group in groups:
        try:
            if media_group:
                await bot.send_media_group(chat_id=group['group_id'], media=media_group)
            else:
                await message.copy_to(chat_id=group['group_id'])
            success_count += 1
        except BotKicked:
            failed_count += 1
            await db.delete_group(group['group_id'])
        if success_count % 1500 == 0:
            await asyncio.sleep(30)
        await asyncio.sleep(0.05)
    return success_count, failed_count
