from aiogram import types
from aiogram.types import ChatPermissions
from aiogram.utils.exceptions import BadRequest
from magic_filter import F

from filters import IsGroupAndBotAdmin
from handlers.admin.group_main import paginate_groups
from keyboards.inline.admin_ibuttons import view_groups_ibutton
from keyboards.inline.user_ibuttons import (
    restrict_messages_ibuttons, text_callback_data, on_off_restrict_ibuttons, restrict_groups_ibutton
)
from loader import dp, bot, db
from utils.user_functions import extracter


# Guruh uchun cheklovlar menyusi
@dp.message_handler(F.text == "✍️ Guruhda xabarlarni cheklash")
async def restrict_messages_main(message: types.Message):
    user_groups = await db.get_group_by_user(telegram_id=message.from_user.id)

    if user_groups:
        extract = extracter(all_datas=user_groups, delimiter=10)
        await message.answer(
            "Ushbu bo'limda guruhingizda foydalanuvchilar uchun turli xil cheklovlarni qo'yishingiz yoki "
            "o'chirishingiz mumkin\n\nKerakli guruh tugmasiga bosing",
            reply_markup=await restrict_groups_ibutton(all_groups=extract[0], current_page=1, all_pages=len(extract))
        )


@dp.callback_query_handler(F.data.startswith("userrestrict:"))
async def user_restrict_handle(call: types.CallbackQuery):
    group_id = call.data.split(":")[1]
    group_name = (await bot.get_chat(group_id)).full_name
    await call.message.edit_text(
        text=f"Guruh: {group_name}\n\nKerakli tugmani bosing",
        reply_markup=restrict_messages_ibuttons(group_id=group_id)
    )


# Callback handler: cheklash turini tanlash
@dp.callback_query_handler(text_callback_data.filter())
async def handle_callback_restrict(call: types.CallbackQuery, callback_data: dict):
    callback_type = callback_data["type"]
    group_id = callback_data["group_id"]

    group_name = (await bot.get_chat(group_id)).full_name
    await call.message.edit_text(
        text=f"Guruh: {group_name}\n\nCheklanayotgan xabar turi: {callback_type.capitalize()}",
        reply_markup=on_off_restrict_ibuttons(callback_type, group_id)
    )


@dp.callback_query_handler(F.data.startswith(("offrestrict", "onrestrict")))
async def handle_restrict_action(call: types.CallbackQuery):
    on_off, restrict_type, group_id = call.data.split(":")
    group_id = int(group_id)
    is_enable = on_off == "onrestrict"

    try:
        # Guruhning joriy ruxsatlarini olish
        chat = await bot.get_chat(chat_id=group_id)
        current_permissions = chat.permissions or ChatPermissions()

        # Ruxsatlarni o'zgartirish
        setattr(current_permissions, restrict_type, is_enable)

        # Yangilangan ruxsatlarni qo'llash
        await bot.set_chat_permissions(
            chat_id=group_id,
            permissions=current_permissions,
            use_independent_chat_permissions=True
        )

        await call.message.edit_text(text="Amaliyot muvaffaqqiyatli bajarildi!")
    except BadRequest as e:
        await call.message.edit_text(text=f"Xatolik yuz berdi: {e}")
    except Exception as e:
        await call.message.edit_text(text=f"Kutilmagan xatolik: {e}")


@dp.callback_query_handler(F.data == "back_restrict")
async def back_restrict_handler(call: types.CallbackQuery):
    user_groups = await db.get_group_by_user(telegram_id=call.from_user.id)

    if user_groups:
        extract = extracter(all_datas=user_groups, delimiter=10)
        await call.message.edit_text(
            text="Ushbu bo'limda guruhingizda foydalanuvchilar uchun turli xil cheklovlarni qo'yishingiz yoki "
                 "o'chirishingiz mumkin\n\nKerakli guruh tugmasiga bosing",
            reply_markup=await restrict_groups_ibutton(all_groups=extract[0], current_page=1, all_pages=len(extract)))

    @dp.callback_query_handler(F.data.startswith(("alert-restrict", "next-restrict", "prev-restrict")))
    async def navigation_callback_restrict(call: types.CallbackQuery):
        print(call.data)
        action, current_page = call.data.split(":")
        current_page = int(current_page)

        if action == "alert-restrict":
            await call.answer(f"Siz {current_page} - sahifadasiz!", show_alert=True)
        else:
            await call.answer(cache_time=0)
            try:
                all_groups = await db.get_groups()
                extract = extracter(all_datas=all_groups, delimiter=10)
                total_pages = len(extract)

                if action == "next-restrict":
                    current_page = current_page + 1 if current_page < total_pages else 1
                elif action == "prev-restrict":
                    current_page = current_page - 1 if current_page > 1 else total_pages

                groups_on_page = extract[current_page - 1]

                await call.message.edit_text(
                    text="Ushbu bo'limda guruhingizda foydalanuvchilar uchun turli xil cheklovlarni qo'yishingiz yoki "
                         "o'chirishingiz mumkin\n\nKerakli guruh tugmasiga bosing",
                    reply_markup=await restrict_groups_ibutton(all_groups=groups_on_page, current_page=current_page,
                                                               all_pages=total_pages))
            except Exception:
                pass
            await call.answer(cache_time=0)
