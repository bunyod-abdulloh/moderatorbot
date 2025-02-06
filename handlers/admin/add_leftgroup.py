from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import Unauthorized

from magic_filter import F

from filters.admins import IsBotAdminFilter
from loader import dp, bot, db
from states.admin import AdminStates


@dp.callback_query_handler(F.data.startswith(("restrictbot:", "leftbot:")))
async def handle_leftbot(call: types.CallbackQuery):
    action, group_id = call.data.split(":")
    group_id = int(group_id)
    await bot.leave_chat(group_id)
    group_name = (await bot.get_chat(group_id)).full_name

    if action == "restrictbot":
        try:
            await db.add_group_to_blacklist(group_id)
        except Unauthorized:
            pass

        await call.message.edit_text(text=f"Bot {group_name} guruhidan chiqarildi va vaqtincha foydalanish cheklandi!")

    if action == "leftbot":
        await db.delete_group(group_id)
        await db.delete_group_from_blacklist(group_id)
        await call.message.edit_text(
            text=f"Bot {group_name} guruhidan chiqarildi va guruh ma'lumotlari ma'lumotlar omboridan o'chirildi!")


@dp.message_handler(IsBotAdminFilter(), F.text == "Botni guruhga qo'shish")
async def handle_add_to_group(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
        text="Guruh usernamesini yuboring"
    )
    await AdminStates.ADD_BOT_TO_GROUP.set()


@dp.message_handler(state=AdminStates.ADD_BOT_TO_GROUP)
async def handle_add_bot_to_group(message: types.Message, state: FSMContext):
    await state.finish()
    try:
        group_username = message.text.split("https://t.me/")[1]
        group = await bot.get_chat(f"@{group_username}")

        await db.delete_group_from_blacklist(group.id)

        await message.answer(f"{group.full_name} guruhi blocklanganlar ro'yxatidan chiqarildi!")
        group_admin = await bot.get_chat_administrators(group.id)

        for admin in group_admin:
            try:
                if admin.user.is_bot:
                    pass
                await bot.send_message(
                    chat_id=admin.user.id,
                    text=f"Botning faoliyati {group.full_name} guruhi uchun tiklandi! Botimizdan foydalanishingiz mumkin!"
                )
            except Exception as err:
                await message.answer(f"{err}\nAdmin: {admin.user.full_name}\nUsername: @{admin.user.username}")
    except Exception as e:
        await message.answer(text=f"Xatolik: {e}")
        return
