from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

REPORT_TYPES = {
    "Тип 1": "report_type_1",
    "Тип 2": "report_type_2",
}


def general_menu():
    btn_about = KeyboardButton(text="🌊 О боте")
    btn_vod_obj = KeyboardButton(text="🤖 ИИ Собеседник")
    btn_faq = KeyboardButton(text="💻 Госуслуги")
    btn_instr = KeyboardButton(text="🛠 Инструменты")
    btn_docs = KeyboardButton(text="📄 Документы")
    btn_contacts = KeyboardButton(text="📞 Контакты")
    btn_priem = KeyboardButton(text="Обратная связь")
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [btn_about, btn_vod_obj],
            [btn_faq, btn_instr],
            [btn_docs, btn_contacts],
            [btn_priem],
        ],
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


def gosuslugi_menu_main():
    btn_doc1 = KeyboardButton(text="""Оптимизированный стандарт""")
    btn_doc2 = KeyboardButton(text="""Описание целевого состояния""")
    btn_back = KeyboardButton(text="""Назад""")
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [btn_doc1],
            [btn_doc2],
            [btn_back],
        ],
        resize_keyboard=True,
    )
    return markup


def reglament_menu():
    btn_doc1 = KeyboardButton(text="""Бюджетные сметы""")
    btn_doc2 = KeyboardButton(text="""Субвенции""")
    btn_doc3 = KeyboardButton(text="""Подведомственные учреждения""")
    btn_doc5 = KeyboardButton(text="""Капитальный ремонт""")
    btn_doc4 = KeyboardButton(text="""Капитальное строительство""")
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


def instruments_menu():
    btn_doc1 = KeyboardButton(text="""Видео / аудио -> протокол""")
    btn_doc3 = KeyboardButton(text="""Стенограмма -> протокол""")
    btn_doc4 = KeyboardButton(text="""Назад""")

    markup = ReplyKeyboardMarkup(
        keyboard=[
            [btn_doc1, btn_doc3],
            [btn_doc4],
        ],
        resize_keyboard=True,
    )
    return markup
