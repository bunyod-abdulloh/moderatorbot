import asyncio
from typing import List

import aiogram
from aiogram import types
from aiogram.dispatcher import FSMContext
from magic_filter import F

from filters.admins import IsBotAdminFilter
from handlers.admin.group_main import warning_text
from keyboards.default.admin_buttons import bot_main_buttons
from loader import dp, db, bot


@dp.message_handler(IsBotAdminFilter(), F.text == "Bot")
async def bot_main_page(message: types.Message):
    await message.answer("Bot bosh sahifasi!", reply_markup=bot_main_buttons)


@dp.message_handler(IsBotAdminFilter(), F.text == "Foydalanuvchilar soni")
async def user_count(message: types.Message):
    count = await db.count_users()
    await message.answer(f"Foydalanuvchilar soni: {count}")


@dp.message_handler(IsBotAdminFilter(), F.text == "✅ Oddiy post yuborish")
async def send_to_bot_users(message: types.Message, state: FSMContext):
    await message.answer(text=warning_text)
    await state.set_state("send_to_bot_users")


@dp.message_handler(state="send_to_bot_users", content_types=types.ContentTypes.ANY)
async def send_to_bot_users_two(message: types.Message, state: FSMContext):
    await db.update_send_status(send_post=True)

    all_users = await db.select_all_users()
    success_count, failed_count = 0, 0

    for index, user in enumerate(all_users, start=1):
        try:
            await message.copy_to(chat_id=user["telegram_id"])
            success_count += 1
        except aiogram.exceptions.BotBlocked:
            failed_count += 1
            await db.delete_user(telegram_id=user["telegram_id"])
        else:
            failed_count += 1
            await db.delete_user(telegram_id=user["telegram_id"])
        if index % 1500 == 0:
            await asyncio.sleep(30)
        await asyncio.sleep(0.05)

    await db.update_send_status(send_post=False)
    await message.answer(
        f"Habar {success_count} ta foydalanuvchiga yuborildi!\n{failed_count} ta foydalanuvchi botni bloklagan."
    )
    await state.finish()


@dp.message_handler(IsBotAdminFilter(), F.text == "🎞 Mediagroup post yuborish")
async def send_media_to_bot(message: types.Message, state: FSMContext):
    await message.answer(text=warning_text)
    await state.set_state("send_to_media_bot")


@dp.message_handler(state="send_to_media_bot", content_types=types.ContentTypes.ANY, is_media_group=True)
async def send_media_to_bot_second(message: types.Message, album: List[types.Message], state: FSMContext):
    media_group = types.MediaGroup()

    for obj in album:
        try:
            file_id = obj.photo[-1].file_id if obj.photo else obj[obj.content_type].file_id
            media_group.attach({
                "media": file_id,
                "type": obj.content_type,
                "caption": obj.caption
            })
        except Exception as err:
            await message.answer(f"Media qo'shishda xato: {err}")
            return

    await db.update_send_status(send_post=True)

    all_users = await db.select_all_users()
    success_count, failed_count = 0, 0

    for index, user in enumerate(all_users, start=1):
        try:
            await bot.send_media_group(chat_id=user['telegram_id'], media=media_group)
            success_count += 1
        except aiogram.exceptions.BotBlocked:
            failed_count += 1
            await db.delete_user(telegram_id=user["telegram_id"])
        else:
            failed_count += 1
            await db.delete_user(telegram_id=user["telegram_id"])
        if index % 1500 == 0:
            await asyncio.sleep(30)
        await asyncio.sleep(0.05)

    await db.update_send_status(send_post=False)
    await message.answer(
        f"Media {success_count} ta foydalanuvchiga yuborildi!\n{failed_count} ta foydalanuvchi botni bloklagan."
    )
    await state.finish()
