import logging
import traceback

cancel_text = "Jarayonni bekor qilish uchun /bekor buyrug'ini kiriting!"


def extracter(all_datas, delimiter):
    empty_list = []
    for e in range(0, len(all_datas), delimiter):
        empty_list.append(all_datas[e:e + delimiter])
    return empty_list


def logging_text(err):
    # Stack trace va xatolik tafsilotlarini log qilish
    logging.error(f"Xatolik: {err}")
    logging.error("Traceback:\n" + traceback.format_exc())