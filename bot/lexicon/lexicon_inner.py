from keyboards.keyboards_inner import general_menu, gosuslugi_menu, reglament_menu, gosuslugi_menu_main, instruments_menu


LEXICON_RU: dict[str, str] = {
    'Видео / аудио -> протокол': ["""🎦  Видео / аудио -> протокол

1. Загрузите аудио / видео / голосовое сообщение
2. Получите стенограмму и протокол 
""", instruments_menu(), []],
    'Стенограмма -> протокол': ["""📄 Стенограмма -> протокол

1. Загрузите текстовый файл
2. Получите протокол
""", instruments_menu(), []],
    'Суммаризация': ["""🔤 Суммаризация

1. Загрузите один или несколько файлов
2. Получите протокол
""", instruments_menu(), []],
    'Документы': ["""📄 Документы

Задайте интересующий вопрос в чате или голосом.

ИИ предоставит ответ на основе документов, содержащихся в базе:
- Водный кодекс
- ПП и регламенты по госуслугам
- регламенты по бюджетным проектировкам
""", general_menu(), []],
    'Инструменты': ["Меню инструментов", instruments_menu(), []],
    'Контакты': ["""📞 Контакты

Здесь вы можете уточнить ФИО, рабочие почту и телефон сотрудников системы Росводресурсов.

Задайте интересующий вопрос в чате или голосом. 
""", general_menu(), []],
    'О боте': ['''🌊 ФАВРик - ИИ ассистент сотрудника Росводресурсов

Помогу вам:
- получить актуальную информацию по госуслугам
- получить оперативную информацию о водохозяйственной обстановке
- найти нужную информацию в нормативном акте Росводресурсов
- уточнить контакты коллег
- подготовить протокол встречи 
и много другое

Если у вас возникли вопросы или нужна помощь, просто напишите нам, и мы с радостью вам ответим!

Техподдрежка: pkidesk@voda.gov.ru, @avilovaks
''', general_menu(), []],
    'ГосУслуги': ["Выберите ГосУслугу:", gosuslugi_menu_main(), []],
    'Назад': ["Возвращаемся к основному меню", general_menu(), []],
    'Обратная связь': ['''Вы хотите сообщить о проблеме или предложить свои идеи? Напишите мне и я обязательно передам вопрос ответственному специалисту!''',None, []],
    'Виртуальный собеседник': ['''Добро пожаловать в чат с искусственным интеллектом! Спрашивайте обо всем, что вас интересует, и я постараюсь ответить!''', None, []],
    'Структура Росводресурсов': ["Структура Росводресурсов:", None, ['/app/documents/struct.png',]],
    'Бюджетные сметы': ['''Для ознакомления с регламентом бюджетных проектировок перейдите по [ссылке](https://disk.yandex.ru/i/ZerDVsaQMgjXIw).''', None, []],
    'Субвенции': ['''Для ознакомления с регламентом бюджетных проектировок перейдите по [ссылке](https://disk.yandex.ru/i/hfpsLDLRwFdilg). ''', None, []],
    'Подведомственные учреждения': ['''Для ознакомления с регламентом бюджетных проектировок перейдите по [ссылке](https://disk.yandex.ru/i/3GXi9BCnroZJrg).''', None, []],
    'Капитальный ремонт': ['''Для ознакомления с регламентом бюджетных проектировок перейдите по [ссылке](https://disk.yandex.ru/i/MT7UNgV3VJpFZw).''', None, []],
    'Капитальное строительство': ['''Для ознакомления с регламентом бюджетных проектировок перейдите по [ссылке](https://disk.yandex.ru/i/47TQvC8K_g4nEw)''', None, []],
    'Регламенты ПКИ': ['''Выберите регламент''', reglament_menu(), []],
    'Электронный протокол': ['''Я умею обрабатывать аудио- и видео файлы и формировать электронный протокол. 

Просто отправьте мне запись вашего совещания размером до 20 Мб и я сформирую электронный протокол для вас.''', None, []],
}

LEXICON_COMMANDS_RU = {
    '/start': ['''Привет, меня зовут ФАВРик, и я ваш помощник от Росводресурсов!  🌊

Я здесь, чтобы помочь вам быстрее и эффективнее справляться с рабочими задачами. Я использую ИИ, чтобы предоставить вам наиболее точную и актуальную информацию.

Помогу вам:
- получить актуальную информацию по госуслугам
- получить оперативную информацию о водохозяйственной обстановке
- найти нужную информацию в нормативном акте Росводресурсов
- уточнить контакты коллег
- подготовить протокол встречи 
и много другое

Если у вас возникли вопросы или нужна помощь, просто напишите нам, и мы с радостью вам ответим!

Спасибо за ваш вклад в сохранение водных ресурсов! 💧

Техподдрежка: pkidesk@voda.gov.ru, @avilovaks
''', general_menu(), []],
    '/clear': ["История диалога очищена", None, []]
}


GOSUSLUGI_LEVEL_1 = {
    'Водный реестр': ['''Оптимизированный стандарт: Государственный водный реестр.''', None, ['/app/documents/ОС2 ГВР 19.04.24.pdf',]],
    '''Право пользования''': ['''Оптимизированный стандарт: Право пользования водными объектами''', None, ['/app/documents/ОС2 Решения 22.07.2024.pdf', ]],
    'Договоры': ['''Оптимизированный стандарт: Договоры водопользования''', None, ['/app/documents/ОС2 Договор 22.07.2024.pdf', ]],
    'Земельный участок': ['''Оптимизированный стандарт: Земельный участок на водном объекте''', None, ['/app/documents/ОС2 ИЗУ 22.07.2024.pdf',]],
    'Допустимые нормы': ['''Оптимизированный стандарт: Допустимые нормы веществ и микроорганизмов''', None, ['/app/documents/ОС2 НДС 22.07.2024.pdf', ]],
}


GOSUSLUGI_LEVEL_2 = {
    'Водный реестр': ['''Описание целевого состояния:\nГосударственный водный реестр.''', None, ['/app/documents/ОЦС2 ГВР 26.05.24.pdf',]],
    '''Право пользования''': ['''Описание целевого состояния:\nПраво пользования водными объектами''', None, ['/app/documents/ОЦС2 Решения 26.04.24.pdf',]],
    'Договоры': ['''Описание целевого состояния:\nДоговоры водопользования''', None, ['/app/documents/ОЦС2 Договор 15.06.24.pdf',]],
    'Земельный участок': ['''Описание целевого состояния:\nЗемельный участок на водном объекте''', None, ['/app/documents/ОЦС2 ИЗУ 26.05.24.pdf',]],
    'Допустимые нормы': ['''Описание целевого состояния:\nДопустимые нормы веществ и микроорганизмов''', None, ['/app/documents/ОЦС2 НДС 26.04.24.pdf',]],
}


INTRO_MESSAGES = [
    "Я умею преобразовывать аудио- и видеофайлы в текстовый формат. Давай вместе попробуем!",
    "Нужно подключиться к закрытому контуру ФАВР? Я могу помочь",
    "Я могу рассказать много интересного о водных ресурсах России!",
    "Ищешь регламенты планирования и контроля исполнения? У меня все есть, могу поделиться 😉",
    "Могу помочь с поисками данных из государственного водного реестра!",
    "Забыл важные детали? Я помогу тебе быстро восстановить информацию из документов!",
]
