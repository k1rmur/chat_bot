from aiogram import Router, F, Bot
from aiogram.types import Message, ChatMemberAdministrator, ChatMemberMember, ChatMemberOwner
from aiogram.filters import CommandStart
from aiogram.enums.parse_mode import ParseMode
from lexicon.lexicon_outer import LEXICON_RU
import logging
from dotenv import load_dotenv, find_dotenv
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import os
from services.rag import query_engine
from services.converter import recognize_voice, clear_temp
from aiogram.types import FSInputFile
from database import Database
from keyboards.keyboards_inner import gosuslugi_menu
from services.log_actions import log_action, allowed_actions
from filters.filters import users_from_group_only, ChatTypeFilter


def stringify_context(
    result: dict,
) -> list[str]:
    """
    Displays given context as a list of strings of size <= 4096 symbols

    Args:
        context: list of documents from RAG chain

    Returns:
        Returns a list of strings that fit into a single telegram message
    """

    chunks = []
    nodes = result.source_nodes
    result = "Источники:\n"
    for idx, doc in enumerate(nodes):
        current_source = ""
        current_source += f"#{idx + 1}\n"
        for metadata_key, metadata_value in doc.metadata.items():
            current_source += str(metadata_key) + ": " + str(metadata_value) + "\n"
        current_source += doc.text + "\n"
        if len(result) + len(current_source) >= 4096:
            chunks.append(result)
            result = current_source
        else:
            result += current_source

    chunks.append(result)


    return chunks

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
    @users_from_group_only
    async def send_optimized_std_menu(message: Message, state: FSMContext):
        await message.answer("Меню ОС:", reply_markup=gosuslugi_menu())
        await state.set_state(UserState.level_1_menu)


    @router.message(F.text=='Описание целевого состояния')
    @users_from_group_only
    async def send_target_state_menu(message: Message, state: FSMContext):
        await message.answer("Меню ОСЦ:", reply_markup=gosuslugi_menu())
        await state.set_state(UserState.level_2_menu)

    
    @router.message(UserState.level_1_menu)
    @users_from_group_only
    async def handle_optimized_std_menu(message: Message, state: FSMContext):
        text = message.text
        if text in GOSUSLUGI_LEVEL_1:
            answer_text, reply_markup, files = GOSUSLUGI_LEVEL_1.get(text)
            await message.answer(answer_text)
            for file in files:
                await message.answer_document(FSInputFile(file, filename=file.split('/')[-1]))
        if text=='Назад':
            answer_text, reply_markup, file = LEXICON_RU.get('Назад')
            await message.answer(answer_text, reply_markup=reply_markup)
            await state.clear()


    @router.message(UserState.level_2_menu)
    @users_from_group_only
    async def handle_target_state_menu(message: Message, state: FSMContext):
        text = message.text
        if text in GOSUSLUGI_LEVEL_2:
            answer_text, reply_markup, files = GOSUSLUGI_LEVEL_2.get(text)
            await message.answer(answer_text)
            for file in files:
                await message.answer_document(FSInputFile(file, filename=file.split('/')[-1]))
        if text=='Назад':
            answer_text, reply_markup, file = LEXICON_RU.get('Назад')
            await message.answer(answer_text, reply_markup=reply_markup)
            await state.clear()


@router.message(CommandStart())
@users_from_group_only
async def process_start_command(message: Message, db: Database):
    try:
    	log_action(message, allowed_actions['start'])
    except Exception as e:
        logger.error(e, exc_info=True)
    logger.info(f'Пользователь {message.from_user.username} начал диалог, код чата {message.chat.id}')
    answer_text, reply_markup, files = LEXICON_COMMANDS_RU['/start']
    await message.answer(answer_text, reply_markup=reply_markup)
    await db.add_user(
        id=message.from_user.id,
        username=message.from_user.username,
    )


@router.message((F.text | F.voice) & ~F.text.startswith('/') & F.text != ADD_USER_PASSWORD & F.chat.type.in_({"private",}))
@users_from_group_only
async def send(message: Message, bot: Bot):
    if message.text in LEXICON_RU:
        log_action(message, allowed_actions['menu'])
        answer_text, reply_markup, files = LEXICON_RU[message.text]


        await message.answer(text=answer_text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
        if files:
            for file in files:
                print(file)
                await message.answer_document(FSInputFile(file, filename=file.split('/')[-1]))
    else:
        log_action(message, allowed_actions['ai'])
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
            chain = await query_engine.aquery(text)
            answer = chain.__str__()
            logger.info(f'Пользователь {message.from_user.username} задал вопрос: "{text}", получен ответ: "{answer}"')
            await message.reply(text=answer, parse_mode=None)
#            chunks = stringify_context(chain)
#            for chunk in chunks:
#                print(chunk)
#                await message.reply(text=chunk, parse_mode=None)
        except Exception as e:
            error_text = f'Пользователь {message.from_user.username} получил ошибку\n{e}'
            logger.error(error_text, exc_info=True)
            await bot.send_message(322077458, error_text)
            await message.reply("Произошла ошибка при обработке Вашего запроса :(")
