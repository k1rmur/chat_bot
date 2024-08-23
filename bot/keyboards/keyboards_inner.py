from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def general_menu():
    btn_vod_obj = KeyboardButton(text="Виртуальный собеседник")
    btn_gouslugi = KeyboardButton(text="Электронный протокол")
    btn_struct_rosvodres = KeyboardButton(text="Регламенты ПКИ")
    btn_faq = KeyboardButton(text="ГосУслуги")
    btn_chs = KeyboardButton(text="Оперативная информация о водохозяйственной обстановке")
    btn_priem = KeyboardButton(text="Обратная связь")
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

def reglament_menu():
    btn_doc1 = KeyboardButton(text='''Бюджетные сметы''')
    btn_doc2 = KeyboardButton(text='''Субвенции''')
    btn_doc3 = KeyboardButton(text='''Подведомственные учреждения''')
    btn_doc5 = KeyboardButton(text='''Капитальный ремонт''')
    btn_doc4 = KeyboardButton(text='''Капитальное строительство''')
    btn_back = KeyboardButton(text='''Назад''')
    markup = ReplyKeyboardMarkup(
        keyboard= [[btn_doc1], [btn_doc2], [btn_doc3], [btn_doc4], [btn_doc5], [btn_back]],
        resize_keyboard=True
    )
    return markup
