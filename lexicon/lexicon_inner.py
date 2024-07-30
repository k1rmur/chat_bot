from keyboards.keyboards_inner import general_menu, gosuslugi_menu, reglament_menu


LEXICON_RU: dict[str, str] = {
    'ГосУслуги': ["Выберите ГосУслугу:", gosuslugi_menu()],
    'Назад': ["Возвращаемся к основному меню", general_menu()],
    'Водный реестр': ['''Государственный водный реестр

Ссылка на заявление: https://www.gosuslugi.ru/609879/1/form. 

Услуга включает подачу в электронной форме заявления на:

1) получение копий документов из государственного водного реестра;

2) получение сведений из государственного водного реестра.''', None],
    'Право пользования': ['''Право пользования водными объектами 
Ссылка на заявление: https://www.gosuslugi.ru/609916/1/form. 

Услуга включает подачу в электронной форме заявления на:

1) получение права пользования водным объектом или его частью на основании решения;

2) внесение изменений в решение на пользование водным объектом путём выдачи нового решения;

3) досрочное прекращение действия решения о предоставлении водного объекта в пользование

Перед тем, как подать заявление, обратитесь за предоставлением государственного водного реестра.''', None],
    'Договоры': ['''Договоры водопользования
Ссылка на заявление: https://www.gosuslugi.ru/609877/1/form. 

Услуга включает подачу в электронной форме заявления на:

1) получение водных объектов в пользование на основании договора водопользования, в том числе по результатам аукциона;

2) передачу прав и обязанностей по договорам водопользования. ''', None],
    'Земельный участок': ['''Земельный участок на водном объекте
Ссылка на заявление: https://www.gosuslugi.ru/609940/1/form

Получить разрешение на создание искусственного земельного участка можно на водном объекте или его части, которые находятся в федеральной собственности. 

Услуга не предназначена для подачи заявления на создание искусственного земельного участка в границах морского порта.''', None],
    'Допустимые нормы': ['''Допустимые нормы веществ и микроорганизмов 
Ссылка на заявление: https://www.gosuslugi.ru/609878/1/form. 

Услуга включает подачу в электронной форме заявления на:

1) утверждение нормативов допустимых сбросов веществ и микроорганизмов;

2) внесение изменений в приказ об утверждении нормативов допустимых сбросов веществ и микроорганизмов.''', None],
    'Обратная связь': ['''Вы хотите сообщить о проблеме или предложить свои идеи? Напишите мне и я обязательно передам вопрос ответственному специалисту!''',None],
    'Виртуальный собеседник': ['''Добро пожаловать в чат с искусственным интеллектом! Спрашивайте обо всем, что вас интересует, и я постараюсь ответить!''', None],
    'Структура Росводресурсов': ["Структура Росводресурсов:", None],
    'Бюджетные сметы': ['''Для ознакомления с регламентом бюджетных проектировок перейдите по [ссылке](https://disk.yandex.ru/i/ZerDVsaQMgjXIw).''', None],
    'Субвенции': ['''Для ознакомления с регламентом бюджетных проектировок перейдите по [ссылке](https://disk.yandex.ru/i/hfpsLDLRwFdilg). ''', None],
    'Субсидии на иные цели': ['''Для ознакомления с регламентом бюджетных проектировок перейдите по [ссылке](https://disk.yandex.ru/i/3GXi9BCnroZJrg).''', None],
    'Капитальный ремонт': ['''Для ознакомления с регламентом бюджетных проектировок перейдите по [ссылке](https://disk.yandex.ru/i/MT7UNgV3VJpFZw).''', None],
    'Капитальное строительство': ['''Для ознакомления с регламентом бюджетных проектировок перейдите по ссылке: ждем ссылку''', None],
    'Регламенты ПКИ': ['''Выберите регламент''', reglament_menu()],
    'Электронный протокол': ['''Я умею обрабатывать аудио- и видео файлы и формировать электронный протокол. 

Просто отправьте мне запись вашего совещания размером до 20 Мб и я сформирую электронный протокол для вас.''', None],
    'Оперативная информация о водохозяйственной обстановке': ['''Ждем''', None],
}

LEXICON_COMMANDS_RU = {
    '/start': ['''Привет, меня зовут ФАВРик, и я ваш помощник от Росводресурсов! 🌊

Я здесь, чтобы помочь вам эффективно управлять водными ресурсами России. Я использую искусственный интеллект, чтобы предоставить вам наиболее точную и актуальную информацию.

Я помогу вам:
•	Найти нужный нормативно правовой акт; 
•	Преобразовать аудио- и видеофайлы в текст и сделать электронный протокол;
•	Оперативно реагировать на информацию о водохозяйственной обстановке. 

Если у вас возникли вопросы или нужна помощь, просто напишите нам, и мы с радостью вам ответим!

Спасибо за ваш вклад в сохранение водных ресурсов России! 💧
''', general_menu()],
    '/clear': ["История диалога очищена", None]
}