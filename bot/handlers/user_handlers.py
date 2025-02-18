import logging
import os

from aiogram import Bot, F, Router
from aiogram.enums.parse_mode import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile, Message
from database import Database
from dotenv import find_dotenv, load_dotenv
from filters.filters import users_from_group_only
from keyboards.keyboards_inner import gosuslugi_menu
from services.log_actions import allowed_actions, log_action
from services.prompt_templates import QUERY_GEN_PROMPT
from services.rag import get_context_str, llm, text_qa_template, get_rag_answer


class UserState(StatesGroup):
    level_1_menu = State()
    level_2_menu = State()


load_dotenv(find_dotenv())
mode = os.getenv("MODE")
print(mode)
ADD_USER_PASSWORD = os.getenv("ADD_USER_PASSWORD")
DOCUMENTS_SENT = "/app/documents_sent"


if mode == "inner":
    from lexicon.lexicon_inner import (
        GOSUSLUGI_LEVEL_1,
        GOSUSLUGI_LEVEL_2,
        LEXICON_COMMANDS_RU,
        LEXICON_RU,
    )
else:
    from lexicon.lexicon_outer import LEXICON_COMMANDS_RU, LEXICON_RU

router = Router()

logger = logging.getLogger(__name__)


if mode == "inner":

    @router.message(F.text == "Оптимизированный стандарт")
    @users_from_group_only
    async def send_optimized_std_menu(message: Message, state: FSMContext):
        await message.answer("Меню ОС:", reply_markup=gosuslugi_menu())
        await state.set_state(UserState.level_1_menu)

    @router.message(F.text == "Описание целевого состояния")
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
                await message.answer_document(
                    FSInputFile(file, filename=file.split("/")[-1])
                )
        if text == "Назад":
            answer_text, reply_markup, file = LEXICON_RU.get("Назад")
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
                await message.answer_document(
                    FSInputFile(file, filename=file.split("/")[-1])
                )
        if text == "Назад":
            answer_text, reply_markup, file = LEXICON_RU.get("Назад")
            await message.answer(answer_text, reply_markup=reply_markup)
            await state.clear()


@router.message(CommandStart())
@users_from_group_only
async def process_start_command(message: Message, db: Database):
    try:
        log_action(message, allowed_actions["start"])
    except Exception as e:
        logger.error(e, exc_info=True)
    logger.info(
        f"Пользователь {message.from_user.username} начал диалог, код чата {message.chat.id}"
    )
    answer_text, reply_markup, files = LEXICON_COMMANDS_RU["/start"]
    await message.answer(answer_text, reply_markup=reply_markup)
    await db.add_user(
        id=message.from_user.id,
        username=message.from_user.username,
    )


@router.message(
    (F.text & ~F.text.startswith("/"))
    & F.chat.type.in_(
        {
            "private",
        }
    )
)
@users_from_group_only
async def send(message: Message, bot: Bot):
    if message.text in LEXICON_RU:
        log_action(message, allowed_actions["menu"])
        answer_text, reply_markup, files = LEXICON_RU[message.text]

        await message.answer(
            text=answer_text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
        )
        if files:
            for file in files:
                print(file)
                await message.answer_document(
                    FSInputFile(file, filename=file.split("/")[-1])
                )
    else:
        text = message.text
        if text is None:
            return

        try:
            answer = await get_rag_answer(text)

            logger.info(
                f'Пользователь {message.from_user.username} задал вопрос: "{text}", получен ответ: "{answer}"'
            )
            log_action(message, allowed_actions["ai"], answer=answer)
            try:
                await message.reply(text=answer, parse_mode="Markdown")
            except TelegramBadRequest:
                await message.reply(text=answer, parse_mode=None)
        except Exception as e:
            error_text = (
                f"Пользователь {message.from_user.username} получил ошибку\n{e}"
            )
            logger.error(error_text, exc_info=True)
            await bot.send_message(322077458, error_text)
            await message.reply("Произошла ошибка при обработке Вашего запроса :(")
