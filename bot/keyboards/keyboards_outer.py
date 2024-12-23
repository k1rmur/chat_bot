from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def general_menu():
    bth_about = KeyboardButton(text="🌊 О боте")
    btn_vod_obj = KeyboardButton(text="🤖 ИИ Собеседник")
    btn_gouslugi = KeyboardButton(text="💻 Госуслуги")
    btn_faq = KeyboardButton(text="Обратная связь")
    btn_priem = KeyboardButton(text="📞 Прием граждан")
    markup = ReplyKeyboardMarkup(
        keyboard=[[bth_about, btn_vod_obj], [btn_gouslugi, btn_priem], [btn_faq]],
        resize_keyboard=True,
    )
    return markup


def gosuslugi_menu():
    btn_doc1 = KeyboardButton(text="""Водный реестр""")
    btn_doc2 = KeyboardButton(text="""Право пользования""")
    btn_doc3 = KeyboardButton(text="""Договоры""")
    btn_doc5 = KeyboardButton(text="""Земельный участок""")
    btn_doc4 = KeyboardButton(text="""Допустимые нормы""")
    btn_back = KeyboardButton(text="""Назад""")
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [btn_doc1],
            [btn_doc2],
            [btn_doc3],
            [btn_doc4],
            [btn_doc5],
            [btn_back],
        ],
        resize_keyboard=True,
    )
    return markup


def inline_rating_keyboard():
    btns = [
        InlineKeyboardButton(text=str(i), callback_data=str(i)) for i in range(1, 11)
    ]
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [btns[0], btns[1]],
            [btns[2], btns[3]],
            [btns[4], btns[5]],
            [btns[6], btns[7]],
            [btns[8], btns[9]],
        ],
        resize_keyboard=True,
    )
    return markup
