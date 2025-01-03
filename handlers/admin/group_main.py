import asyncio
from typing import List

import aiogram
from aiogram import types
from aiogram.dispatcher import FSMContext
from magic_filter import F

from filters.admins import IsBotAdminFilter
from keyboards.default.admin_buttons import group_main_buttons
from keyboards.inline.admin_ibuttons import view_groups_ibutton, group_button
from loader import dp, bot, db
from states.admin import AdminStates

WARNING_TEXT = (
    "Habar yuborishdan oldin postingizni yaxshilab tekshirib oling!\n\n"
    "Imkoni bo'lsa postingizni oldin tayyorlab olib keyin yuboring.\n\n"
    "Habaringizni kiriting:"
)


async def get_group_info(group_id):
    chat = await bot.get_chat(chat_id=group_id)
    return {
        "name": chat.full_name,
        "username": chat.username,
        "member_count": await bot.get_chat_member_count(chat_id=group_id)
    }


async def handle_media_group(album: List[types.Message]) -> types.MediaGroup:
    media_group = types.MediaGroup()
    for obj in album:
        file_id = obj.photo[-1].file_id if obj.photo else obj[obj.content_type].file_id
        media_group.attach({"media": file_id, "type": obj.content_type, "caption": obj.caption})
    return media_group


@dp.message_handler(IsBotAdminFilter(), F.text == "Guruhlar")
async def groups_handler(message: types.Message):
    await message.answer(text=message.text, reply_markup=group_main_buttons)


@dp.message_handler(IsBotAdminFilter(), F.text == "Guruhlar haqida")
async def groups_info_handler(message: types.Message):
    await message.answer(
        text="Kerakli guruh tugmasiga bosing", reply_markup=await view_groups_ibutton()
    )


@dp.callback_query_handler(F.data.startswith("getgroup_"))
async def get_groups_handler(call: types.CallbackQuery):
    group_id = int(call.data.split("_")[1])
    group_info = await get_group_info(group_id)
    await call.message.edit_text(
        text=(
            f"Guruh ma'lumotlari:\n\n"
            f"Guruh nomi: {group_info['name']}\n"
            f"Guruh username: @{group_info['username']}\n"
            f"Foydalanuvchilar soni: {group_info['member_count']}"
        ),
        reply_markup=group_button(group_id=group_id)
    )


@dp.callback_query_handler(F.data.startswith("send_post_to_group:"))
async def send_to_group_handler(call: types.CallbackQuery, state: FSMContext):
    group_id = call.data.split(":")[1]
    await state.update_data(group_id=group_id)
    await call.message.edit_text(text=WARNING_TEXT)
    await AdminStates.SEND_POST_TO_GROUP.set()


@dp.message_handler(state=AdminStates.SEND_POST_TO_GROUP, content_types=types.ContentTypes.ANY)
async def send_to_group_two(message: types.Message, state: FSMContext):
    data = await state.get_data()
    group_id = int(data.get("group_id"))
    try:
        await message.copy_to(chat_id=group_id)
        group_name = (await bot.get_chat(chat_id=group_id)).full_name
        await message.answer(f"{group_name} ga habar yuborildi!")
    except aiogram.exceptions.BotKicked:
        await db.delete_group(group_id)
    await state.finish()


@dp.callback_query_handler(F.data.startswith("send_media_to_group:"))
async def send_media_to_group_handler(call: types.CallbackQuery, state: FSMContext):
    if await db.get_send_status():
        await call.message.edit_text(
            "Xabar yuborish jarayoni yoqilgan! Hisobot kelganidan so'ng xabar yuborishingiz mumkin!"
        )
    else:
        group_id = int(call.data.split(":")[1])
        await state.update_data(group_id=group_id)
        await call.message.edit_text(text=WARNING_TEXT)
        await AdminStates.SEND_MEDIA_TO_GROUP.set()


@dp.message_handler(state=AdminStates.SEND_MEDIA_TO_GROUP, is_media_group=True)
async def send_media_to_group_two(message: types.Message, album: List[types.Message], state: FSMContext):
    try:
        media_group = await handle_media_group(album)
    except Exception as err:
        await message.answer(f"Media qo'shishda xatolik!: {err}")
        return

    data = await state.get_data()
    group_id = int(data["group_id"])
    try:
        await bot.send_media_group(chat_id=group_id, media=media_group)
    except aiogram.exceptions.BotKicked:
        await db.delete_group(group_id)
        await message.answer("Guruh botni bloklagan!")
    await state.finish()


async def send_to_groups(message: types.Message, groups: List[dict], media_group=None):
    success_count, failed_count = 0, 0
    for group in groups:
        try:
            if media_group:
                await bot.send_media_group(chat_id=group['group_id'], media=media_group)
            else:
                await message.copy_to(chat_id=group['group_id'])
            success_count += 1
        except aiogram.exceptions.BotKicked:
            failed_count += 1
            await db.delete_group(group['group_id'])
        if success_count % 1500 == 0:
            await asyncio.sleep(30)
        await asyncio.sleep(0.05)
    return success_count, failed_count


@dp.message_handler(IsBotAdminFilter(), F.text == "🧑💻 Oddiy habar yuborish")
async def send_to_bot_users_handler(message: types.Message):
    if await db.get_send_status():
        await message.answer(
            "Xabar yuborish jarayoni yoqilgan! Hisobot kelganidan so'ng xabar yuborishingiz mumkin!"
        )
    else:
        await message.answer(text=WARNING_TEXT)
        await AdminStates.SEND_POST_TO_GROUPS.set()


@dp.message_handler(state=AdminStates.SEND_POST_TO_GROUPS, content_types=types.ContentTypes.ANY)
async def send_to_bot_users_two(message: types.Message, state: FSMContext):
    groups = await db.get_groups()
    success_count, failed_count = await send_to_groups(message, groups)
    await message.answer(
        f"Xabar {success_count} ta guruhga yuborildi!\n{failed_count} ta guruh botni block qilgan"
    )
    await db.update_send_status(False)
    await state.finish()


@dp.message_handler(IsBotAdminFilter(), F.text == "🖇 Mediagroup habar yuborish")
async def send_media_to_groups_handler(message: types.Message):
    if await db.get_send_status():
        await message.answer(
            "Xabar yuborish jarayoni yoqilgan! Hisobot kelganidan so'ng xabar yuborishingiz mumkin!"
        )
    else:
        await message.answer(text=WARNING_TEXT)
        await AdminStates.SEND_MEDIA_TO_GROUPS.set()


@dp.message_handler(state=AdminStates.SEND_MEDIA_TO_GROUPS, is_media_group=True, content_types=types.ContentTypes.ANY)
async def send_media_to_groups_two(message: types.Message, album: List[types.Message], state: FSMContext):
    try:
        media_group = await handle_media_group(album)
    except Exception as err:
        await message.answer(f"Media qo'shishda xatolik!:\n{err}")
        return

    groups = await db.get_groups()
    success_count, failed_count = await send_to_groups(message, groups, media_group)
    await message.answer(
        f"Media {success_count} ta guruhga yuborildi!\n{failed_count} ta guruh botni block qilgan"
    )
    await db.update_send_status(False)
    await state.finish()
