from keyboards.keyboards_outer import general_menu, gosuslugi_menu

LEXICON_RU: dict[str, str] = {
    "🌊 О боте": [
        """🌊 AI FAVR bot - ИИ-бот, который расскажет о водных ресурсах России, проконсультирует по вопросам оказания госуслуг

Официальный сайт: voda.gov.ru
E-mail: pkidesk@voda.gov.ru
""",
        general_menu(),
        [],
    ],
    "💻 Госуслуги": ["Выберите ГосУслугу:", gosuslugi_menu(), []],
    "Назад": ["Возвращаемся к основному меню", general_menu(), []],
    "Водный реестр": [
        """Государственный водный реестр

Ссылка на заявление: https://www.gosuslugi.ru/609879/1/form. 

Услуга включает подачу в электронной форме заявления на:

1) получение копий документов из государственного водного реестра;

2) получение сведений из государственного водного реестра.""",
        None,
        [],
    ],
    "Право пользования": [
        """Право пользования водными объектами 
Ссылка на заявление: https://www.gosuslugi.ru/609916/1/form. 

Услуга включает подачу в электронной форме заявления на:

1) получение права пользования водным объектом или его частью на основании решения;

2) внесение изменений в решение на пользование водным объектом путём выдачи нового решения;

3) досрочное прекращение действия решения о предоставлении водного объекта в пользование

Перед тем, как подать заявление, обратитесь за предоставлением государственного водного реестра.""",
        None,
        [],
    ],
    "Договоры": [
        """Договоры водопользования
Ссылка на заявление: https://www.gosuslugi.ru/609877/1/form. 

Услуга включает подачу в электронной форме заявления на:

1) получение водных объектов в пользование на основании договора водопользования, в том числе по результатам аукциона;

2) передачу прав и обязанностей по договорам водопользования. """,
        None,
        [],
    ],
    "Земельный участок": [
        """Земельный участок на водном объекте
Ссылка на заявление: https://www.gosuslugi.ru/609940/1/form

Получить разрешение на создание искусственного земельного участка можно на водном объекте или его части, которые находятся в федеральной собственности. 

Услуга не предназначена для подачи заявления на создание искусственного земельного участка в границах морского порта.""",
        None,
        [],
    ],
    "Допустимые нормы": [
        """Допустимые нормы веществ и микроорганизмов 
Ссылка на заявление: https://www.gosuslugi.ru/609878/1/form. 

Услуга включает подачу в электронной форме заявления на:

1) утверждение нормативов допустимых сбросов веществ и микроорганизмов;

2) внесение изменений в приказ об утверждении нормативов допустимых сбросов веществ и микроорганизмов.""",
        None,
        [],
    ],
    "📞 Прием граждан": [
        """Если вы хотите записаться на личный прием к сотрудникам Росводресурсов, обратитесь к сервису ["Прием граждан"](https://external-services.favr.ru/). 

Если вы хотите подать обращение, обратитесь к сервису обратной связи - [ПОС](https://pos.gosuslugi.ru/form/?opaId=348141&utm_source=vk3&utm_medium=1323055&utm_campaign=1022900545183).  

Контакты Федерального агентства водных ресурсов:
🗺️ Адрес: Москва, ул. Кедрова, дом. 8, корп. 1 
⏰ Режим работы: пн-чт: 9:00-18:00, пт: 9:00-16:45

📱Телефон: 8 (499) 125-52-79

📬 E-mail: news@voda.gov.ru

💻 Сайт Росводресурсов: https://voda.gov.ru""",
        None,
        [],
    ],
    "Обратная связь": [
        """Вы хотите сообщить о проблеме или предложить свои идеи? Напишите мне и я обязательно передам вопрос ответственному специалисту!""",
        None,
        [],
    ],
    "🤖 ИИ Собеседник": [
        """Добро пожаловать в чат с искусственным интеллектом! Спрашивайте обо всем, что вас интересует, и я постараюсь ответить!""",
        None,
        [],
    ],
    #    'Структура Росводресурсов': ["Структура Росводресурсов:", None, ['/app/documents/struct.png', ]],
    #    'Информация о ЧС': ['Ждём', None, []]
}

LEXICON_COMMANDS_RU = {
    "/start": [
        """Добро пожаловать в официальный телеграмм-бот Росводресурсов! 🌊

Мы рады приветствовать вас и готовы помочь с любыми вопросами, связанными с водными ресурсами. Этот бот использует ИИ, чтобы предоставлять наиболее точную и актуальную информацию. 

Здесь вы можете:
- получить на консультацию по госуслугам
- записаться на личный прием в Росводресурсы
- получить информацию из открытых источников
- пообщаться с ИИ ассистентом о водных ресурсах России

Если у вас возникли вопросы или нужна помощь, просто напишите нам, и мы с радостью ответим!

Спасибо, что выбрали нас! 💧
""",
        general_menu(),
        [],
    ],
    "/clear": ["История диалога очищена", None, []],
}


INTRO_MESSAGES = [
    "Я могу рассказать много интересного о водных ресурсах России!",
    "Могу помочь с поисками данных из государственного водного реестра!",
    "Расскажу актуальную информацию о чрезвычайных ситуациях Российской Федерации в сфере водных ресурсов.",
    "Готов помочь найти нужную услугу на ГосУслуг!",
    "Ищешь информацию о реках и водоёмах России? Я могу помочь с самыми свежими данными!",
    "Знаком с экосистемами водоемов? Я расскажу о разнообразии российских вод!",
    "Давай обсудим, как улучшить управление водными ресурсами? У меня есть идеи и ресурсы!",
]
