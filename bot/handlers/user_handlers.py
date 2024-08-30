from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.enums.parse_mode import ParseMode
from lexicon.lexicon_outer import LEXICON_RU
import logging
from dotenv import load_dotenv, find_dotenv
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import os
from services.rag import index
from services.converter import recognize_voice, clear_temp
from aiogram.types import FSInputFile
from database import Database
from keyboards.keyboards_inner import gosuslugi_menu


class UserState(StatesGroup):
    level_1_menu = State()
    level_2_menu = State()


load_dotenv(find_dotenv())
mode = os.getenv("MODE")
print(mode)
ADD_USER_PASSWORD = os.getenv("ADD_USER_PASSWORD")
DOCUMENTS_SENT = "/app/documents_sent"


if mode == 'inner':
    from lexicon.lexicon_inner import LEXICON_RU, LEXICON_COMMANDS_RU, GOSUSLUGI_LEVEL_1, GOSUSLUGI_LEVEL_2
else:
    from lexicon.lexicon_outer import LEXICON_RU, LEXICON_COMMANDS_RU

router = Router()

logger = logging.getLogger(__name__)


if mode == 'inner':
    @router.message(F.text=='Оптимизированный стандарт')
    async def send_optimized_std_menu(message: Message, state: FSMContext):
        await message.answer("Меню ОС:", reply_markup=gosuslugi_menu())
        await state.set_state(UserState.level_1_menu)


    @router.message(F.text=='Описание целевого состояния')
    async def send_target_state_menu(message: Message, state: FSMContext):
        await message.answer("Меню ОСЦ:", reply_markup=gosuslugi_menu())
        await state.set_state(UserState.level_2_menu)


@router.message(CommandStart())
async def process_start_command(message: Message, db: Database):
    logger.info(f'Пользователь {message.from_user.username} начал диалог, код чата {message.chat.id}')
    answer_text, reply_markup, files = LEXICON_COMMANDS_RU['/start']
    await message.answer(answer_text, reply_markup=reply_markup)
    await db.add_user(
        id=message.from_user.id,
        username=message.from_user.username,
    )


@router.message((F.text | F.voice) & ~F.text.startswith('/') & F.text != ADD_USER_PASSWORD)
async def send(message: Message, bot: Bot):
    session_id = message.from_user.id

#    if message.text == 'Оптимизированный стандарт':
#        await send_optimized_std_menu(message)
#    elif message.text == 'Описание целевого состояния':
#        await send_target_state_menu(message)
#
    if message.text in LEXICON_RU:
        answer_text, reply_markup, files = LEXICON_RU[message.text]

        # Оперативная информация - загружаем последний отправленный документ
        if message.text=='Оперативная информация о водохозяйственной обстановке':
            if mode == 'inner':
                answer_text= 'Последняя информация:'
                files = filter(os.path.isfile, os.listdir(DOCUMENTS_SENT))
                files = [os.path.join(DOCUMENTS_SENT, f) for f in files]
                if files:
                    files.sort(key=lambda x: os.path.getmtime(x))
                    files = [files[-1],]
            else:
                answer_text = 'Недоступно'

        await message.answer(text=answer_text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
        if files:
            for file in files:
                print(file)
                await message.answer_document(FSInputFile(file, filename=file.split('/')[-1]))
    else:
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
            chain = await index.aquery(text)
            answer = chain.__str__()
            logger.info(f'Пользователь {message.from_user.username} задал вопрос: "{text}", получен ответ: "{answer}"')
            await message.reply(text=answer, parse_mode=None)
        except Exception as e:
            error_text = f'Пользователь {message.from_user.username} получил ошибку\n{e}'
            logger.error(error_text, exc_info=True)
            await bot.send_message(322077458, error_text)
            await message.reply("Произошла ошибка при обработке Вашего запроса :(")



if mode == 'inner':
    @router.message(UserState.level_1_menu)
    async def handle_optimized_std_menu(message: Message, state: FSMContext):
        await message.answer('Провалились')
        text = message.text
        if text in GOSUSLUGI_LEVEL_1:
            answer_text, reply_markup, file = GOSUSLUGI_LEVEL_1.get(text)
        await message.answer(answer_text)
        await message.answer_document(FSInputFile(file, filename=file.split('/')[-1]))
        if text=='Назад':
            answer_text, reply_markup, file = LEXICON_RU.get(text)
            await message.answer(answer_text, reply_markup=reply_markup)
            await state.clear()


    @router.message(UserState.level_2_menu)
    async def handle_target_state_menu(message: Message, state: FSMContext):
        await message.answer('Провалились')
        text = message.text
        if text in GOSUSLUGI_LEVEL_2:
            answer_text, reply_markup, file = GOSUSLUGI_LEVEL_2.get(text)
        await message.answer(answer_text)
        await message.answer_document(FSInputFile(file, filename=file.split('/')[-1]))
        if text=='Назад':
            answer_text, reply_markup, file = LEXICON_RU.get(text)
            await message.answer(answer_text, reply_markup=reply_markup)
            await state.clear()