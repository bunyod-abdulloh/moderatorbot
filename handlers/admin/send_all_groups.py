import asyncio
import logging
from typing import List

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import BotKicked
from magic_filter import F

from filters.admins import IsBotAdminFilter
from handlers.admin.group_main import WARNING_TEXT
from loader import dp, db, bot
from states.admin import AdminStates


async def send_to_groups(message: types.Message, groups: List[dict], media_group: types.MediaGroup = None):
    """
    Guruhlarga oddiy xabar yoki media xabar yuborish.
    """
    success_count, failed_count = 0, 0

    for group in groups:
        try:
            if media_group:
                await bot.send_media_group(chat_id=group['group_'], media=media_group)
            else:
                await message.copy_to(chat_id=group['group_'])
            success_count += 1
        except BotKicked:
            failed_count += 1
            await db.delete_group(group['group_'])
        except Exception as err:
            await message.answer(text=f"Error: {err}\nGroup ID: {group['group_']}")
        if success_count % 1500 == 0:
            await asyncio.sleep(30)
        await asyncio.sleep(0.05)
    return success_count, failed_count


@dp.message_handler(IsBotAdminFilter(), F.text == "🧑‍💻 Oddiy habar yuborish")
async def handle_send_to_groups(message: types.Message, state: FSMContext):
    await state.finish()
    send_status = await db.get_send_status()
    if send_status is True:
        await message.answer("Xabar yuborish jarayoni yoqilgan! Hisobot kelganidan so'ng xabar yuborishingiz mumkin!")
    else:
        groups = await db.get_groups()
        if groups:
            await message.answer(text=WARNING_TEXT)
            await AdminStates.SEND_POST_TO_GROUPS.set()
        else:
            await message.answer("Guruhlar mavjud emas!")


@dp.message_handler(state=AdminStates.SEND_POST_TO_GROUPS, content_types=types.ContentTypes.ANY)
async def handle_send_to_groups_two(message: types.Message, state: FSMContext):
    await state.finish()
    groups = await db.get_groups()
    await db.update_send_status(True)
    success, failed = await send_to_groups(message, groups)
    await db.update_send_status(False)
    await message.answer(text=f"Xabar yuborilgan guruhlar soni: {success}\n"
                              f"Yuborilmaganlar: {failed}")


@dp.message_handler(IsBotAdminFilter(), F.text == "🖇 Mediagroup habar yuborish")
async def handle_send_media_to_groups(message: types.Message, state: FSMContext):
    await state.finish()
    send_status = await db.get_send_status()
    if send_status is True:
        await message.answer("Xabar yuborish jarayoni yoqilgan! Hisobot kelganidan so'ng xabar yuborishingiz mumkin!")
    else:
        groups = await db.get_groups()
        if groups:
            await message.answer(text=WARNING_TEXT)
            await AdminStates.SEND_MEDIA_TO_GROUPS.set()
        else:
            await message.answer("Guruhlar mavjud emas!")


@dp.message_handler(state=AdminStates.SEND_MEDIA_TO_GROUPS, is_media_group=True, content_types=types.ContentTypes.ANY)
async def handle_send_media_to_groups_two(message: types.Message, album: List[types.Message], state: FSMContext):
    await state.finish()
    try:
        media_group = types.MediaGroup()

        for obj in album:
            file_id = obj.photo[-1].file_id if obj.photo else obj[obj.content_type].file_id
            media_group.attach(
                {"media": file_id, "type": obj.content_type, "caption": obj.caption}
            )

    except Exception as err:
        await message.answer(f"Media qo'shishda xatolik!: {err}")
        return

    groups = await db.get_groups()

    await db.update_send_status(True)
    success, failed = await send_to_groups(message, groups, media_group)
    await db.update_send_status(False)
    await message.answer(text=f"Mediagroup yuborilgan guruhlar soni: {success}\n"
                              f"Yuborilmaganlar: {failed}")
