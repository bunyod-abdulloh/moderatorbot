from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

user_main_dbuttons = ReplyKeyboardMarkup(resize_keyboard=True)
user_main_dbuttons.row("➕ Guruhda odam ko'paytirish")
user_main_dbuttons.row("📱 Admin bilan aloqa", "⚙️ Sozlamalar")
