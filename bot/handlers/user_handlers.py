from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from aiogram.enums.parse_mode import ParseMode
from lexicon.lexicon_outer import LEXICON_RU
from langchain_community.chat_message_histories import ChatMessageHistory
import logging
from dotenv import load_dotenv, find_dotenv
import os
from services.rag import conversation_history, conversational_rag_chain
from services.converter import recognize_voice, clear_temp
from aiogram.types import FSInputFile
from database import Database


fire_list = ['ГосУслуги', 'Оптимизированный стандарт', 'Описание целевого состояния', 'Назад', 'Водный реестр', 'Право пользования', 'Договоры', 'Земельный участок', 'Допустимые нормы', 'Обратная связь', 'Виртуальный собеседник', 'Структура Росводресурсов', 'Бюджетные сметы', 'Субвенции', 'Субсидии на иные цели', 'Капитальный ремонт', 'Капитальное строительство', 'Регламенты ПКИ', 'Электронный протокол', 'Оперативная информация о водохозяйственной обстановке']
load_dotenv(find_dotenv())
mode = os.getenv("MODE")
print(mode)
ADD_USER_PASSWORD = os.getenv("ADD_USER_PASSWORD")

if mode == 'inner':
    from lexicon.lexicon_inner import LEXICON_RU, LEXICON_COMMANDS_RU
else:
    from lexicon.lexicon_outer import LEXICON_RU, LEXICON_COMMANDS_RU

router = Router()

logger = logging.getLogger(__name__)

@router.message(CommandStart())
async def process_start_command(message: Message, db: Database):
    logger.info(f'Пользователь {message.from_user.username} начал диалог, код чата {message.chat.id}')
    answer_text, reply_markup = LEXICON_COMMANDS_RU['/start']
    await message.answer(answer_text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    await db.add_user(
        id=message.from_user.id,
        username=message.from_user.username,
    )


@router.message(Command("clear"))
async def process_clear_command(message: Message):
    user_id = message.from_user.id
    conversation_history[user_id] = ChatMessageHistory()
    logger.info(f'Пользователь {message.from_user.username} очистил историю диалога')
    await message.answer(text=LEXICON_COMMANDS_RU['/clear'])


@router.message((F.text | F.voice) & ~F.text.startswith('/') & F.text != ADD_USER_PASSWORD & ~F.text.in_(fire_list))
async def send(message: Message, bot: Bot):
    print("Вызвали send")
    session_id = message.from_user.id
    if message.text in LEXICON_RU:
        if mode=='outer':
            answer_text, reply_markup = LEXICON_RU[message.text]
            await message.answer(text=answer_text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
            if 'Структура Росводресурсов'.lower() in message.text.lower():
                await message.answer_photo(FSInputFile('/app/documents/struct.png'))
    else:
        session_id = message.from_user.id
        if message.voice:
            try:
                file_id = message.voice.file_id
                file = await bot.get_file(file_id=file_id)
                file_path = file.file_path
                audio_destination = f'./tmp/{file_id}.wav'
                await bot.download_file(file_path, audio_destination)
                text = await recognize_voice(file_id)
                clear_temp()
            except Exception as e:
                await message.reply("Произошла ошибка при распознавании голосового сообщения :(")
                logger.error(e, exc_info=True)
                clear_temp()
                return
        else:
            text = message.text
            if text is None:
                return

        try:
            chain = await conversational_rag_chain.ainvoke(
                {"input": text},
                config={
                    "configurable": {"session_id": session_id}
                }
            )
            answer = chain["answer"]
            print(chain["context"])
            logger.info(f'Пользователь {message.from_user.username} задал вопрос: "{text}", получен ответ: "{answer}"')
            await message.reply(text=answer, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            error_text = f'Пользователь {message.from_user.username} получил ошибку\n{e}'
            logger.error(error_text, exc_info=True)
            await bot.send_message(322077458, error_text)
            await message.reply("Произошла ошибка при обработке Вашего запроса :(")



if mode=='inner':
    from keyboards.keyboards_inner import gosuslugi_menu, gosuslugi_menu_main, general_menu, reglament_menu
    @router.message(F.text.in_(fire_list))
    async def send_text(message: Message, bot: Bot):
        print("Меня вызвали")
        global menu_lvl
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
            bot.send_document(message.chat.id, FSInputFile('/app/documents/ОС2 ГВР 19.04.24.pdf'))
        elif message.text == '''Право пользования''' and menu_lvl == 2:
            bot.send_message(message.chat.id, '''Оптимизированный стандарт: Право пользования''')
            bot.send_document(message.chat.id, FSInputFile('/app/documents/ОС2 Решения 22.07.2024.pdf'))
        elif message.text == 'Договоры' and menu_lvl == 2:
            bot.send_message(message.chat.id, '''Оптимизированный стандарт: Договоры водопользования''')
            bot.send_document(message.chat.id, FSInputFile('/app/documents/ОС2 Договор 22.07.2024.pdf'))
        elif message.text == 'Земельный участок' and menu_lvl == 2:
            bot.send_message(message.chat.id, '''Оптимизированный стандарт: Искусственный  земельный участок''')
            bot.send_document(message.chat.id, FSInputFile('/app/documents/ОС2 ИЗУ 22.07.2024.pdf'))
        elif message.text == 'Допустимые нормы' and menu_lvl == 2:
            bot.send_message(message.chat.id, '''Оптимизированный стандарт: Допустимые нормы веществ и микроорганизмов''')
            bot.send_document(message.chat.id, FSInputFile('/app/documents/ОС2 НДС 22.07.2024.pdf'))
        elif message.text == 'Водный реестр' and menu_lvl == 3:
            bot.send_message(message.chat.id, '''Описание целевого состояния: Государственный водный реестр''')
            bot.send_document(message.chat.id, FSInputFile('/app/documents/ОЦС2 ГВР 26.05.24.pdf'))
        elif message.text == '''Право пользования''' and menu_lvl == 3:
            bot.send_message(message.chat.id, '''Описание целевого состояния: Право пользования''')
            bot.send_document(message.chat.id, FSInputFile('/app/documents/ОЦС2 Решения 26.04.24.pdf'))
        elif message.text == 'Договоры' and menu_lvl == 3:
            bot.send_message(message.chat.id, '''Описание целевого состояния: Договоры водопользования''')
            bot.send_document(message.chat.id, FSInputFile('/app/documents/ОЦС2 Договор 15.06.24.pdf'))
        elif message.text == 'Земельный участок' and menu_lvl == 3:
            bot.send_message(message.chat.id, '''Описание целевого состояния: Искусственный  земельный участок''')
            bot.send_document(message.chat.id, FSInputFile('/app/documents/ОЦС2 ИЗУ 26.05.24.pdf'))
        elif message.text == 'Допустимые нормы' and menu_lvl == 3:
            bot.send_message(message.chat.id, '''Описание целевого состояния:  Допустимые нормы веществ и микроорганизмов''')
            bot.send_document(message.chat.id, FSInputFile('/app/documents/ОЦС2 НДС 26.04.24.pdf'))
        elif message.text == 'Обратная связь':
            bot.send_message(message.chat.id, '''Вы хотите сообщить о проблеме или предложить свои идеи? Напишите мне и я обязательно передам вопрос ответственному специалисту!''')
        elif message.text == 'Виртуальный собеседник':
            bot.send_message(message.chat.id, '''Добро пожаловать в чат с искусственным интеллектом! Спрашивайте обо всем, что вас интересует, и я постараюсь ответить!''')
        elif message.text == 'Структура Росводресурсов':
            bot.send_message(message.chat.id, "Структура Росводресурсов:")
            bot.send_photo(message.chat.id, photo=FSInputFile('/app/documents/struct.png'))
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

    Просто отправьте мне запись вашего совещания размером до 2 Гб и я сформирую электронный протокол для вас.''', parse_mode='Markdown')
        elif message.text == 'Оперативная информация о водохозяйственной обстановке':
            bot.send_message(message.chat.id, '''Ждем''', parse_mode='Markdown') 
