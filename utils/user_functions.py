import logging
import traceback

from data.config import ADMIN_GROUP_ID
from loader import bot

cancel_text = "Jarayonni bekor qilish uchun /bekor buyrug'ini kiriting!"


def extracter(all_datas, delimiter):
    empty_list = []
    for e in range(0, len(all_datas), delimiter):
        empty_list.append(all_datas[e:e + delimiter])
    return empty_list


async def logging_text(err):
    # Stack trace va xatolik tafsilotlarini log qilish
    logging.error(f"Xatolik: {err}")
    logging.error("Traceback:\n" + traceback.format_exc())
    error_text = f"Xatolik:\n{err}\n\nTraceback:\n" + traceback.format_exc()
    await bot.send_message(
        chat_id=ADMIN_GROUP_ID, text=error_text
    )
