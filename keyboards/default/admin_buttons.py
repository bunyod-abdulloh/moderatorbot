from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

admin_main_buttons = ReplyKeyboardMarkup(resize_keyboard=True)
admin_main_buttons.row("Bot", "Guruhlar")
admin_main_buttons.row(KeyboardButton("Bosh sahifa"))

bot_main_buttons = ReplyKeyboardMarkup(resize_keyboard=True)
bot_main_buttons.row("Foydalanuvchilar soni")
bot_main_buttons.row("✅ Oddiy post yuborish")
bot_main_buttons.row("🎞 Mediagroup post yuborish")
bot_main_buttons.row("🔙 Ortga")

group_main_buttons = ReplyKeyboardMarkup(resize_keyboard=True)
group_main_buttons.row("Guruhlar haqida")
group_main_buttons.row("🧑‍💻 Oddiy habar yuborish")
group_main_buttons.row("🖇 Mediagroup habar yuborish")
group_main_buttons.row("🔙 Ortga")
