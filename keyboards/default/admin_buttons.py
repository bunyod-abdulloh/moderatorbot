from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def create_keyboard(buttons, row_width=1, resize=True):
    """
    Tugmalarni generatsiya qilish uchun funksiya.

    :param buttons: Tugmalar matnining ro'yxati
    :param row_width: Qator bo'yicha tugmalar soni
    :param resize: Klaviaturani o'lchamini o'zgartirish
    :return: ReplyKeyboardMarkup obyekt
    """
    markup = ReplyKeyboardMarkup(resize_keyboard=resize, row_width=row_width)
    for row in buttons:
        markup.row(*[KeyboardButton(text) for text in row])
    return markup


# Admin asosiy tugmalari
admin_main_buttons = create_keyboard([
    ["Bot", "Guruhlar"],
    ["Bosh sahifa"]
])

# Bot bo'limi tugmalari
bot_main_buttons = create_keyboard([
    ["Foydalanuvchilar soni"],
    ["✅ Oddiy post yuborish", "🎞 Mediagroup post yuborish"],
    ["⭐️ Havolalar"],
    ["🔙 Ortga"]
])

# Guruh bo'limi tugmalari
group_main_buttons = create_keyboard([
    ["Guruhlar haqida", "Botni guruhga qo'shish"],
    ["🧑‍💻 Oddiy habar yuborish", "🖇 Mediagroup habar yuborish"],
    ["🔙 Ortga"]
])

referrals_buttons = create_keyboard([
    ["➕ Qo'shish", "🔎 Barchasini ko'rish"],
    ["Kechagi takliflar soni"],
    ["🔙 Ortga"]
]
)
