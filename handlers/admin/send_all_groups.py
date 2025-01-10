from aiogram import types
from aiogram.dispatcher import FSMContext
from magic_filter import F

from loader import dp, db, bot


@dp.message_handler(F.text == "Guruhlar haqida")
async def groups_info_handler(message: types.Message, state: FSMContext):
    await state.finish()
    all_groups = await db.get_groups()

    if not all_groups:
        await message.answer("Guruhlar mavjud emas!")
    else:
        groups_list = []

        # for group in all_groups:
        group_name = (await bot.get_chat(all_groups[0]['group_id'])).title
        group_username = f"@{(await bot.get_chat(all_groups[0]['group_id'])).username}"
        count_members = await bot.get_chat_member_count(all_groups[0]['group_id'])
        user_first_name = (await bot.get_chat(all_groups[0]['telegram_id'])).first_name
        user_username = f"@{(await bot.get_chat(all_groups[0]['telegram_id'])).username}"
        user_status = (await bot.get_chat_member(all_groups[0]['group_id'], all_groups[0]['telegram_id'])).status
        print(group_name)
    # await message.answer(
    #     text="Guruhlar haqida tugmasiga bosing", reply_markup=await view_groups_ibutton()
    # )
