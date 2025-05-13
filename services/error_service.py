import sys
import traceback

from data.config import ADMIN_GROUP


async def notify_exception_to_admin(err: Exception):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    tb = traceback.extract_tb(exc_tb)[-1]

    filename = tb.filename.split("/")[-1]
    func_name = tb.name
    line_no = tb.lineno
    error_type = exc_type.__name__

    error_message = (
        f"⚠️ Xatolik yuz berdi:\n\n"
        f"📄 Fayl: {filename}\n"
        f"🔧 Funksiya: {func_name}()\n"
        f"📌 Qator: {line_no}\n"
        f"❗ Xatolik turi: {error_type}\n"
        f"🧨 Xatolik matni: {err}"
    )
    from loader import bot
    await bot.send_message(chat_id=ADMIN_GROUP, text=error_message)