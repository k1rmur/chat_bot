from keyboards.keyboards_inner import gosuslugi_menu, gosuslugi_menu_main, general_menu, reglament_menu
from aiogram import Router, F, Bot
from aiogram.types import Message
import logging
from aiogram.types import FSInputFile

router = Router()

logger = logging.getLogger(__name__)

fire_list = ['ГосУслуги', 'Оптимизированный стандарт', 'Описание целевого состояния', 'Назад', 'Водный реестр', 'Право пользования', 'Договоры', 'Земельный участок', 'Допустимые нормы', 'Обратная связь', 'Виртуальный собеседник', 'Структура Росводресурсов', 'Бюджетные сметы', 'Субвенции', 'Субсидии на иные цели', 'Капитальный ремонт', 'Капитальное строительство', 'Регламенты ПКИ', 'Электронный протокол', 'Оперативная информация о водохозяйственной обстановке']

lower_list = [x.lower() for x in fire_list]

menu_lvl = 0

@router.message(F.text.lower().in_(lower_list))
async def send_text(message: Message, bot: Bot):
    global menu_lvl
    if message.text.lower() in lower_list:
        if message.text == 'ГосУслуги':
            menu_lvl = 1
            bot.send_message(message.chat.id, "Выберите ОС или ОСЦ:", reply_markup=gosuslugi_menu_main())
        elif message.text == 'Оптимизированный стандарт':
            menu_lvl = 2
            bot.send_message(message.chat.id, "Выберите ГосУслугу", reply_markup=gosuslugi_menu())
        elif message.text == 'Описание целевого состояния':
            menu_lvl = 3
            bot.send_message(message.chat.id, "Выберите ГосУслугу", reply_markup=gosuslugi_menu())
        elif message.text == 'Назад':
            bot.send_message(message.chat.id, "Возвращаемся к основному меню", reply_markup=general_menu())
            menu_lvl = 0
        elif message.text == 'Водный реестр' and menu_lvl == 2:
            bot.send_message(message.chat.id, '''Оптимизированный стандарт: Государственный водный реестр''')
            bot.send_document(message.chat.id, FSInputFile('./app/documents/ОС2 ГВР 19.04.24.pdf', 'rb'))
        elif message.text == '''Право пользования''' and menu_lvl == 2:
            bot.send_message(message.chat.id, '''Оптимизированный стандарт: Право пользования''')
            bot.send_document(message.chat.id, FSInputFile('./app/documents/ОС2 Решения 22.07.2024.pdf', 'rb'))
        elif message.text == 'Договоры' and menu_lvl == 2:
            bot.send_message(message.chat.id, '''Оптимизированный стандарт: Договоры водопользования''')
            bot.send_document(message.chat.id, FSInputFile('./app/documents/ОС2 Договор 22.07.2024.pdf', 'rb'))
        elif message.text == 'Земельный участок' and menu_lvl == 2:
            bot.send_message(message.chat.id, '''Оптимизированный стандарт: Искусственный  земельный участок''')
            bot.send_document(message.chat.id, FSInputFile('./app/documents/ОС2 ИЗУ 22.07.2024.pdf', 'rb'))
        elif message.text == 'Допустимые нормы' and menu_lvl == 2:
            bot.send_message(message.chat.id, '''Оптимизированный стандарт: Допустимые нормы веществ и микроорганизмов''')
            bot.send_document(message.chat.id, FSInputFile('./app/documents/ОС2 НДС 22.07.2024.pdf', 'rb'))
        elif message.text == 'Водный реестр' and menu_lvl == 3:
            bot.send_message(message.chat.id, '''Описание целевого состояния: Государственный водный реестр''')
            bot.send_document(message.chat.id, FSInputFile('./app/documents/ОЦС2 ГВР 26.05.24.pdf', 'rb'))
        elif message.text == '''Право пользования''' and menu_lvl == 3:
            bot.send_message(message.chat.id, '''Описание целевого состояния: Право пользования''')
            bot.send_document(message.chat.id, FSInputFile('./app/documents/ОЦС2 Решения 26.04.24.pdf', 'rb'))
        elif message.text == 'Договоры' and menu_lvl == 3:
            bot.send_message(message.chat.id, '''Описание целевого состояния: Договоры водопользования''')
            bot.send_document(message.chat.id, FSInputFile('./app/documents/ОЦС2 Договор 15.06.24.pdf', 'rb'))
        elif message.text == 'Земельный участок' and menu_lvl == 3:
            bot.send_message(message.chat.id, '''Описание целевого состояния: Искусственный  земельный участок''')
            bot.send_document(message.chat.id, FSInputFile('./app/documents/ОЦС2 ИЗУ 26.05.24.pdf', 'rb'))
        elif message.text == 'Допустимые нормы' and menu_lvl == 3:
            bot.send_message(message.chat.id, '''Описание целевого состояния:  Допустимые нормы веществ и микроорганизмов''')
            bot.send_document(message.chat.id, FSInputFile('./app/documents/ОЦС2 НДС 26.04.24.pdf', 'rb'))
        elif message.text == 'Обратная связь':
            bot.send_message(message.chat.id, '''Вы хотите сообщить о проблеме или предложить свои идеи? Напишите мне и я обязательно передам вопрос ответственному специалисту!''')
        elif message.text == 'Виртуальный собеседник':
            bot.send_message(message.chat.id, '''Добро пожаловать в чат с искусственным интеллектом! Спрашивайте обо всем, что вас интересует, и я постараюсь ответить!''')
        elif message.text == 'Структура Росводресурсов':
            bot.send_message(message.chat.id, "Структура Росводресурсов:")
            bot.send_photo(message.chat.id, photo=FSInputFile('./app/documents/struct.png', 'rb'))
        elif message.text == 'Бюджетные сметы':
            bot.send_message(message.chat.id, '''Для ознакомления с регламентом бюджетных проектировок перейдите по [ссылке](https://disk.yandex.ru/i/ZerDVsaQMgjXIw).''', parse_mode='Markdown')
        elif message.text == 'Субвенции':
            bot.send_message(message.chat.id, '''Для ознакомления с регламентом бюджетных проектировок перейдите по [ссылке](https://disk.yandex.ru/i/hfpsLDLRwFdilg). ''', parse_mode='Markdown')
        elif message.text == 'Субсидии на иные цели':
            bot.send_message(message.chat.id, '''Для ознакомления с регламентом бюджетных проектировок перейдите по [ссылке](https://disk.yandex.ru/i/3GXi9BCnroZJrg).''', parse_mode='Markdown')
        elif message.text == 'Капитальный ремонт':
            bot.send_message(message.chat.id, '''Для ознакомления с регламентом бюджетных проектировок перейдите по [ссылке](https://disk.yandex.ru/i/MT7UNgV3VJpFZw).''', parse_mode='Markdown')
        elif message.text == 'Капитальное строительство':
            bot.send_message(message.chat.id, '''Для ознакомления с регламентом бюджетных проектировок перейдите по ссылке: ждем ссылку''', parse_mode='Markdown')
        elif message.text == 'Регламенты ПКИ':
            bot.send_message(message.chat.id, '''Выберите регламент''', parse_mode='Markdown', reply_markup=reglament_menu())
        elif message.text == 'Электронный протокол':
            bot.send_message(message.chat.id, '''Я умею обрабатывать аудио- и видео файлы и формировать электронный протокол. 

    Просто отправьте мне запись вашего совещания размером до 20 Мб и я сформирую электронный протокол для вас.''', parse_mode='Markdown')
        elif message.text == 'Оперативная информация о водохозяйственной обстановке':
            bot.send_message(message.chat.id, '''Ждем''', parse_mode='Markdown') 