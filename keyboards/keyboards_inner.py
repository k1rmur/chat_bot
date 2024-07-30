from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def general_menu():
    btn_vod_obj = KeyboardButton("Виртуальный собеседник")
    btn_gouslugi = KeyboardButton("Электронный протокол")
    btn_struct_rosvodres = KeyboardButton("Регламенты ПКИ")
    btn_faq = KeyboardButton("ГосУслуги")
    btn_chs = KeyboardButton("Оперативная информация о водохозяйственной обстановке")
    btn_priem = KeyboardButton("Обратная связь")
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
    markup = ReplyKeyboardMarkup(
        keyboard= [[btn_doc1], [btn_doc2], [btn_doc3], [btn_doc4], [btn_doc5], [btn_back]],
        resize_keyboard=True
    )
    return markup

def reglament_menu():
    btn_doc1 = KeyboardButton('''Бюджетные сметы''')
    btn_doc2 = KeyboardButton('''Субвенции''')
    btn_doc3 = KeyboardButton('''Субсидии на иные цели''')
    btn_doc5 = KeyboardButton('''Капитальный ремонт''')
    btn_doc4 = KeyboardButton('''Капитальное строительство''')
    btn_back = KeyboardButton('''Назад''')
    markup = ReplyKeyboardMarkup(
        keyboard= [[btn_doc1], [btn_doc2], [btn_doc3], [btn_doc4], [btn_doc5], [btn_back]],
        resize_keyboard=True
    )
    return markup