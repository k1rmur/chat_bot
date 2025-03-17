REFINE_ORDERS_PROMPT = """Перед тобой несколько списков поручений сотрудникам, извлеченных из разных частей стенограммы. Твоя задача:

1. Объединить все поручения в один список, оставить только самые важные.
2. Удалить дубликаты поручений, если они присутствуют.
3. Сгруппировать поручения по сотрудникам и датам, чтобы они были представлены последовательно и структурировано.

Вот списки поручений:

-------------
{input}
-------------

Если список поручений не пуст, выведи результат в виде структурированного списка следующей формы:

◦Сотрудник: [имя или номер в стенограмме]
◦Список поручений:
    - [Суть поручения]
    - Дата выполнения: [дата, к которой необходимо выполнить поручение, если обговорено]

Не используй MarkDown, не дублируй информацию, не добавляй своих комментариев, если поручений нет, не пиши ничего.

Список поручений:

"""

REFINE_CONTENT_PROMPT = """Перед тобой несколько списков тем разговора и принятых решений, извлеченных из разных частей стенограммы. Твоя задача:

1. Объединить все темы в один список, оставляя только наиболее выжные из них.
2. Удалить дубликаты тем и решений, если они присутствуют.
3. Сгруппировать темы и решения в логическом порядке, чтобы они были представлены последовательно и структурировано.

Вот списки тем:

-------------
{input}
-------------

Если список тем не пуст, выведи результат в виде структурированного списка следующей формы:

◦Тема обсуждения: [краткая тема]
◦Описание: [пересказ реплик участников совещания по этой теме, не менее 5 предложений]
◦Решения: [принятые решения по данной теме]

Не используй MarkDown, не дублируй информацию, не добавляй своих комментариев, если ничего нет, ничего не пиши.

Ключевые темы разговора и соответствующие им решения:
                                                     
"""

EXTRACT_MAIN_QUESTIONS_PROMPT = """Твоя задача — выделить основную тему обсуждения, которая была ключевой в ходе совещания, то есть главную тему или проблему, которая обсуждалась наиболее подробно или имела наибольшее значение для участников.

Вот суммаризованные списки:

-------------
{input}
-------------

Выдели одну основную тему совещания, если списки пустые, не выводи ничего.

Основная тема совещания:

"""

EXTRACT_SHORT_RESUME_PROMPT = """У тебя есть суммаризованные списки тем разговора, принятых решений и поручений сотрудникам, которые были извлечены и сгруппированы из стенограммы совещания. Твоя задача:

1. Сформировать краткое резюме совещания, включающее основные темы, принятые решения и поручения сотрудникам, но кратко и по существу.
2. Убедись, что резюме передает основную суть совещания без избыточных деталей.

Вот суммаризованные списки:

-------------
{input}
-------------

Выведи краткое резюме совещания, не используя MarkDown, не дублируй информацию, не добавляй своих комментариев. Если списки пустые, не пиши ничего.

Краткое резюме:

"""

CONTENT_PROMPT = """Извлеки только самые важные темы разговора и соответствующие им решения, используя только (!) информацию из следующей стенограммы:

-------------
{chunk}
-------------

Обеспечь полноту и точность извлеченной информации, не используй MarkDown, не дублируй информацию, не добавляй своих комментариев, если пусто, не пиши ничего.

Формат ответа:

◦Тема обсуждения: [краткая тема]
◦Описание: [пересказ реплик участников совещания по этой теме, не менее 5 предложений]
◦Решения: [принятые решения по данной теме]

Самые важные темы разговора и соответствующие им решения:

"""

ORDER_PROMPT = """Извлеки список поручений сотрудникам, используя только (!) информацию из следующей стенограммы, если она пустая, ничего не пиши. Вот стенограмма:

-------------
{chunk}
-------------

Составь список в формате:

◦Сотрудник: [имя или номер в стенограмме]
◦Поручение: [Суть поручения]
◦Дата, к которой нужно выполнить поручение [Дата, если обговорена]

Обеспечь полноту и точность извлеченной информации, не дублируй информацию, не используй MarkDown, не добавляй своих комментариев.

Список поручений:

"""


REFINE_PROMPT_STR = (
    "У нас есть возможность улучшить оригинальный ответ "
    "(если необходимо) с помощью контекста внизу.\n"
    '"""\n'
    "{context_msg}\n"
    '"""\n'
    "Используя новый контекст, улучши оригинальный ответ "
    "ответь на вопрос: {query_str}."
    "Если контекст не помогает, выведи предыдущий ответ.\n"
    "Оригинальный Ответ: {existing_answer}\n"
)

QA_PROMPT_STR = (
    "Контекст дан снизу.\n"
    '"""\n'
    "{context_str}\n"
    '"""\n'
    "Используя в первую очередь информацию из контекста, а не априорные знания, "
    "ответь на вопрос: {query_str}\n. Если в контексте нет ответа, ответь самостоятельно, не добавляя комментариев о том, что информации нет в контексте. Не сообщай имя файла, откуда взял информацию и не добавляй лишних коментариев, например 'в контексте указано, что'."
)

QA_SYSTEM_PROMPT = "Ты бот-ассистент Федерального агенства по водным ресурсам (ФАВР), задача которого отвечать на вопросы по контексту из базы данных, переданному тебе. Ты можешь использовать любую информацию из контекста для ответа, в том числе контактные данные сотрудников и информацию о законах."

QUERY_GEN_PROMPT = (
    "Ты бот-ассистент Федерального агенства по водным ресурсам (ФАВР), который на основе вопроса пользователя генерирует "
    "поисковый запрос к базе данных. Этот запрос должен содержать ВСЮ смысловую информацию и быть достаточно коротким, не содержать лишних слов. "
    '"""\n'
    "Вот несколько примеров:\n\n"
    "Вопрос: Расскажи мне о реке Волга\n"
    "Поисковый запрос: Река Волга\n\n"
    "Вопрос: Что сказано в Статье 3 Водного кодекса?\n"
    "Поисковый запрос: Водный кодекс Статья 3\n\n"
    "Вопрос: Мне нужен номер приемной руководителя\n"
    "Поисковый запрос: Приемная руководителя, телефон\n\n"
    "Вопрос: Дай мне информацию о сотруднике Иванове Иване\n"
    "Поисковый запрос: Иванов Иван\n\n"
    "Вопрос: На сколько лет заключается договор водопользования?\n"
    "Поисковый запрос: Срок договора водопользования\n\n"
    '"""\n'
    "Вопрос: {query}\n"
    "Поисковый запрос: "
)
