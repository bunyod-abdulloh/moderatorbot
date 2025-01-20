from aiogram import types
from aiogram.dispatcher import FSMContext
from magic_filter import F

from filters.admins import IsBotAdminFilter
from keyboards.default.admin_buttons import referrals_buttons
from keyboards.inline.admin_ibuttons import view_referrals_ibutton, back_to_ref_main
from loader import dp, db, bot
from states.admin import AdminStates
from utils.user_functions import extracter


async def paginate_referrals(call: types.CallbackQuery, current_page: int, next_page=False, prev_page=False):
    """
    Helper function to paginate referrals and show next/previous pages.

    Args:
        call (types.CallbackQuery): The callback query object containing the user's interaction.
        current_page (int): The current page number.
        next_page (bool, optional): Flag indicating whether to go to the next page. Defaults to False.
        prev_page (bool, optional): Flag indicating whether to go to the previous page. Defaults to False.
    """
    all_groups = await db.get_all_referrals()
    extract = extracter(all_datas=all_groups, delimiter=10)
    total_pages = len(extract)

    # Adjust the current page based on user actions
    if next_page and current_page < total_pages:
        current_page += 1
    elif prev_page and current_page > 1:
        current_page -= 1

    groups_on_page = extract[current_page - 1]
    markup = await view_referrals_ibutton(groups_on_page, current_page, total_pages)
    try:
        await call.answer(cache_time=0)
        await call.message.edit_text("Kerakli tugmani bosing", reply_markup=markup)
    except Exception:
        pass


@dp.message_handler(IsBotAdminFilter(), F.text == "⭐️ Havolalar", state="*")
async def referral_handler_main(message: types.Message, state: FSMContext):
    """
    Handler to show the main referral page when the admin presses the "Havolalar" button.
    """
    await state.finish()
    await message.answer(text=message.text, reply_markup=referrals_buttons)


@dp.message_handler(IsBotAdminFilter(), F.text == "➕ Qo'shish", state="*")
async def create_referral_handle(message: types.Message, state: FSMContext):
    """
    Handler to prompt the admin to input referral text when pressing the "Qo'shish" button.
    """
    await state.finish()
    await message.answer(
        text="Havola matnini yuboring\n\nEslatma: matnda faqat kichik lotin harflari va _ + - * : kabi belgilardan "
             "foydalanish mumkin!"
    )
    await AdminStates.ADD_REFERRAL.set()


@dp.message_handler(state=AdminStates.ADD_REFERRAL)
async def add_referral_handle(message: types.Message, state: FSMContext):
    """
    Handler to add a referral when the admin submits the referral text.
    """
    await db.add_referral(message.text)
    await message.answer("Havola qo'shildi!")
    await state.finish()


@dp.message_handler(IsBotAdminFilter(), F.text == "🔎 Barchasini ko'rish", state="*")
async def all_referrals_handle(message: types.Message, state: FSMContext):
    """
    Handler to display all referrals when the admin presses the "Barchasini ko'rish" button.
    """
    await state.finish()
    referrals = await db.get_all_referrals()
    if not referrals:
        await message.answer("Havolalar mavjud emas!")
        return

    extract = extracter(referrals, 10)
    markup = await view_referrals_ibutton(extract[0], current_page=1, all_pages=len(extract))
    await message.answer(text=message.text, reply_markup=markup)


@dp.callback_query_handler(F.data.startswith(("ref:prev_", "ref:alert_", "ref:next_")))
async def referrals_action_handle(call: types.CallbackQuery):
    """
    Handler for pagination actions (next, previous, or alert) in the referral list.
    """
    action, current_page = call.data.split("_")
    current_page = int(current_page)

    if action == "ref:alert":
        await call.answer(f"Siz {current_page} - sahifadasiz!", show_alert=True)
    else:
        await paginate_referrals(
            call, current_page, next_page=(action == "ref:next"), prev_page=(action == "ref:prev")
        )


@dp.callback_query_handler(F.data.startswith("getreferral_"))
async def get_referral_handler(call: types.CallbackQuery):
    """
    Handler to show detailed information of a specific referral when clicked.
    """
    referral_id = int(call.data.split("_")[1])
    referral = await db.get_referral_by_id(referral_id)
    bot_username = (await bot.me).username

    ref_name = f"https://t.me/{bot_username}?start={referral['name']}"
    await call.message.edit_text(
        text=f"Havola nomi: {ref_name}\n"
             f"Havola qo'shilgan sana: {referral['created_at']}\n"
             f"Takliflar soni: {referral['amount']}",
        reply_markup=back_to_ref_main(ref_id=referral_id)
    )


@dp.callback_query_handler(F.data.startswith("ref:del_"))
async def delete_referrals_handler(call: types.CallbackQuery):
    """
    Handler to delete a referral when the admin clicks the delete button.

    This handler is triggered when the admin clicks the delete button associated with a specific referral.
    It extracts the referral ID from the callback data, deletes the corresponding referral from the database,
    and then returns to the main referral page. A confirmation message is sent to the admin with an alert.

    Args:
        call (types.CallbackQuery): The callback query object containing the user's interaction.
    """
    # Extract referral ID from callback data
    referral_id = int(call.data.split("_")[1])

    # Delete the referral from the database using the extracted ID
    await db.delete_referral_by_id(referral_id)

    # Return to the main referral page
    await back_to_ref_main_handler(call)

    # Send confirmation alert to the admin
    await call.answer(text="Referral deleted!", show_alert=True)


@dp.callback_query_handler(F.data == "back_to_ref_main")
async def back_to_ref_main_handler(call: types.CallbackQuery):
    """
    Handler to return to the main referral page when the "Back" button is clicked.
    """
    referrals = await db.get_all_referrals()

    extract = extracter(referrals, 10)
    markup = await view_referrals_ibutton(extract[0], current_page=1, all_pages=len(extract))
    await call.message.edit_text(
        text="Havolalar bosh sahifasi", reply_markup=markup
    )


@dp.message_handler(IsBotAdminFilter(), F.text == "Bugungi takliflar soni")
async def today_referrals_count(message: types.Message):
    """
    Handler to display the count of today's referrals.
    """
    count_invites = await db.get_today_referrals()
    total_invites = ""

    for invite in count_invites:
        total_invites += f"{invite['name']}: {invite['total_invites']}\n"

    await message.answer(text=f"Bugungi takliflar:\n\n{total_invites}", reply_markup=back_to_ref_main())
