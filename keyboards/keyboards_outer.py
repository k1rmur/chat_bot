from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def general_menu():
    btn_vod_obj = KeyboardButton("Виртуальный собеседник")
    btn_gouslugi = KeyboardButton("ГосУслуги")
    btn_struct_rosvodres = KeyboardButton("Структура Росводресурсов")
    btn_faq = KeyboardButton("Обратная связь")
    btn_chs = KeyboardButton("Информация о ЧС")
    btn_priem = KeyboardButton("Прием граждан")
    markup = ReplyKeyboardMarkup(
        keyboard= [[btn_vod_obj], [btn_gouslugi], [btn_chs], [btn_struct_rosvodres], [btn_priem], [btn_faq]],
        resize_keyboard=True
    )
    return markup 

def gosuslugi_menu():
    btn_doc1 = KeyboardButton('''Водный реестр''')
    btn_doc2 = KeyboardButton('''Право пользования''')
    btn_doc3 = KeyboardButton('''Договоры''')
    btn_doc5 = KeyboardButton('''Земельный участок''')
    btn_doc4 = KeyboardButton('''Допустимые нормы''')
    btn_back = KeyboardButton('''Назад''')
    markup.add(btn_doc1, btn_doc2, btn_doc3, btn_doc4, btn_doc5, btn_back)
    markup = ReplyKeyboardMarkup(
        keyboard= [[btn_doc1], [btn_doc2], [btn_doc3], [btn_doc4], [btn_doc5], [btn_back]],
        resize_keyboard=True
    )
    return markup