from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup


def general_menu():
    btn_vod_obj = KeyboardButton(text="Виртуальный собеседник")
    btn_gouslugi = KeyboardButton(text="ГосУслуги")
    btn_struct_rosvodres = KeyboardButton(text="Структура Росводресурсов")
    btn_faq = KeyboardButton(text="Обратная связь")
    btn_chs = KeyboardButton(text="Информация о ЧС")
    btn_priem = KeyboardButton(text="Прием граждан")
    markup = ReplyKeyboardMarkup(
        keyboard= [[btn_vod_obj], [btn_gouslugi], [btn_chs], [btn_struct_rosvodres], [btn_priem], [btn_faq]],
        resize_keyboard=True
    )
    return markup 

def gosuslugi_menu():
    btn_doc1 = KeyboardButton(text='''Водный реестр''')
    btn_doc2 = KeyboardButton(text='''Право пользования''')
    btn_doc3 = KeyboardButton(text='''Договоры''')
    btn_doc5 = KeyboardButton(text='''Земельный участок''')
    btn_doc4 = KeyboardButton(text='''Допустимые нормы''')
    btn_back = KeyboardButton(text='''Назад''')
    markup = ReplyKeyboardMarkup(
        keyboard= [[btn_doc1], [btn_doc2], [btn_doc3], [btn_doc4], [btn_doc5], [btn_back]],
        resize_keyboard=True
    )
    return markup


def inline_rating_keyboard():

    btns = [[InlineKeyboardButton(text=str(i), callback_data=str(i)),] for i in range(1,11)]
    markup = InlineKeyboardMarkup(
        inline_keyboard=btns,
        resize_keyboard=True
    )
    return markup
