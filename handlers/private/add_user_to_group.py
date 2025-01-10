from aiogram import types
from aiogram.dispatcher import FSMContext
from magic_filter import F

from keyboards.inline.user_ibuttons import add_user_to_group_ibuttons, get_groups_ibuttons
from loader import dp, db
from states.user import UserStates
from utils.user_functions import cancel_text


async def handle_user_groups(call: types.CallbackQuery, toggle: bool):
    """User groups handling logic."""
    user_groups = await db.get_group_by_user(telegram_id=call.from_user.id)
    if user_groups:
        await call.message.edit_text(
            text="Guruhingizni tanlang",
            reply_markup=await get_groups_ibuttons(user_groups, toggle)
        )
    else:
        await call.message.edit_text(text="Sizda bot qo'shilgan guruh mavjud emas!")


@dp.message_handler(F.text == "➕ Guruhda odam ko'paytirish", state="*")
async def add_user_to_group(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
        text=(
            "Bu funksiya orqali guruhingizga endi kirgan odam xabar jo'nata olmaydi, "
            "xabar jo'natish uchun guruhingizga odam qo'shishi kerak bo'ladi. "
            "Xizmatni ishlatish uchun bot guruhingizda admin bo'lishi lozim! "
            "Yoqish tugmasini bosishdan oldin botni guruhingizga admin qiling!"
        ),
        reply_markup=add_user_to_group_ibuttons
    )


@dp.callback_query_handler(F.data == "on_increase")
async def add_user_to_group_callback(call: types.CallbackQuery):
    await handle_user_groups(call, toggle=False)


@dp.callback_query_handler(F.data.startswith("increase_on:"))
async def user_group_callback(call: types.CallbackQuery, state: FSMContext):
    group_id = int(call.data.split(":")[1])
    get_group = await db.get_group(group_id)

    if get_group['users'] > 0:
        await call.message.edit_text(
            text=f"Xizmat yoqilgan! Qo'shiladigan odam soni: {get_group['users']}"
        )
    else:
        await state.update_data(group_id=group_id)
        await call.message.edit_text(
            text=(
                f"Guruhingizga nechta odam qo'shilganidan so'ng xabar yuborish ochilishini istaysiz?\n"
                f"{cancel_text}\n\nIltimos, faqat raqam kiriting"
            )
        )
        await UserStates.NUMBER_OF_USERS.set()


@dp.message_handler(state=UserStates.NUMBER_OF_USERS)
async def number_of_users_handle(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        data = await state.get_data()
        await db.update_add_user(int(message.text), data['group_id'])
        await message.answer("Kiritgan ma'lumotlaringiz saqlandi!")
        await state.finish()
    else:
        await message.answer(text="Iltimos, faqat raqam kiriting!")


@dp.callback_query_handler(F.data == "off_increase")
async def off_add_user_callback(call: types.CallbackQuery):
    await handle_user_groups(call, toggle=True)


@dp.callback_query_handler(F.data.startswith("increase_off:"))
async def increase_off_handle(call: types.CallbackQuery):
    group_id = int(call.data.split(":")[1])
    await db.update_add_user(0, group_id)
    await call.message.edit_text(text="Xizmat o'chirildi!")
