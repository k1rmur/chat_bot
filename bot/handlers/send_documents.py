import asyncio
import json
import logging
import os
import random
import re
from datetime import datetime

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram_calendar import DialogCalendar, DialogCalendarCallback
from database import Database
from docx import Document
from filters.filters import allowed_users_only
from services.map_reduce_docs import clear_temp
from services.map_reduce_news import return_news_summary
from services.text_extraction import extract_news_from_document
from sqlalchemy.ext.asyncio import AsyncSession

DOCUMENTS_TO_SEND = "/app/documents_to_send"
SEND_TO_FILE = "/app/send_to/send_to_list.json"

mode = os.getenv("MODE")

if mode == "inner":
    from lexicon.lexicon_inner import INTRO_MESSAGES
else:
    from lexicon.lexicon_outer import INTRO_MESSAGES


logger = logging.getLogger(__name__)


router = Router()

ADD_USER_PASSWORD = os.getenv("ADD_USER_PASSWORD")


class DocumentStates(StatesGroup):
    waiting_for_document = State()
    waiting_for_password = State()
    waiting_for_text = State()
    waiting_for_rating = State()
    waiting_for_text_for_subscribers = State()


def load_send_to():
    if os.path.exists(SEND_TO_FILE):
        with open(SEND_TO_FILE, "r") as f:
            return json.load(f)
    return []


def save_send_to(send_to):
    with open(SEND_TO_FILE, "w") as f:
        json.dump(send_to, f)


send_to = load_send_to()


@router.message(Command("help"))
@allowed_users_only
async def help_command(message: Message):
    help_text = """
Доступные команды:
/help - Показать список доступных команд
/send_document - Отправить новый документ
/check_documents - Проверить список документов в папке для отправки
/subscribe - Добавить себя в список рассылки (требуется пароль)
/send_to_subscribers - Отправить сообщение подписанным на рассылку
/get_report - Получить отчет
    """
    await message.reply(help_text)


@router.message(Command("statistics"))
@allowed_users_only
async def statistics(message: Message):
    await message.reply_document(FSInputFile("/app/logs/stats.csv"))


@router.message(Command("subscribe"))
async def add_user_command(message: Message, state: FSMContext):
    await message.reply("Пожалуйста, введите пароль для добавления в список рассылки.")
    await state.set_state(DocumentStates.waiting_for_password)


@router.message(Command("send_to_everyone"))
@allowed_users_only
async def process_send_command(message: Message, state: FSMContext):
    await message.reply("Пожалуйста, напишите текст для рассылки всем пользователям.")
    await state.set_state(DocumentStates.waiting_for_text)


@router.message(Command("send_to_subscribers"))
@allowed_users_only
async def process_send_command_to_subscribers(message: Message, state: FSMContext):
    await message.reply("Пожалуйста, напишите текст для рассылки всем подписанным.")
    await state.set_state(DocumentStates.waiting_for_text_for_subscribers)


@router.message(DocumentStates.waiting_for_text)
async def send_to_everyone(message: Message, db: Database, state: FSMContext):
    if message.text:
        result = await db.get_chat_ids()
        tasks = [
            message.bot.send_message(chat_id=chat_id, text=message.text)
            for chat_id in result
        ]
        await asyncio.gather(*tasks)
        await message.reply("Рассылка прошла успешно.")
    else:
        await message.reply("Нет текста.")
    await state.clear()


@router.message(DocumentStates.waiting_for_text_for_subscribers)
async def send_to_subscribers(message: Message, db: Database, state: FSMContext):
    if message.text:
        result = load_send_to()
        tasks = [
            message.bot.send_message(chat_id=chat_id, text=message.text)
            for chat_id in result
        ]
        await asyncio.gather(*tasks)
        await message.reply("Рассылка прошла успешно.")
    else:
        await message.reply("Нет текста.")
    await state.clear()


@router.message(DocumentStates.waiting_for_password)
async def handle_password(message: Message, state: FSMContext):
    if message.text == ADD_USER_PASSWORD:
        user_id = message.from_user.id
        if user_id not in send_to:
            send_to.append(user_id)
            save_send_to(send_to)
            await message.reply("Вы успешно добавлены в список рассылки.")
        else:
            await message.reply("Вы уже находитесь в списке рассылки.")
    else:
        await message.reply("Неверный пароль. Вы не добавлены в список рассылки.")
    await state.clear()


@router.message(Command("send_document"))
@allowed_users_only
async def send_document_command(message: Message, state: FSMContext):
    await message.reply(
        "Пожалуйста, отправьте документ.\nЕго имя должно быть в формате DD_MM_YYYY_{другая информация}.расширение"
    )
    await state.set_state(DocumentStates.waiting_for_document)


@router.message(Command("get_report"))
async def get_report_command(message: Message):
    if message.from_user.id in load_send_to():
        await message.answer(
            "Пожалуйста, выберите дату.",
            reply_markup=await DialogCalendar().start_calendar(year=2024),
        )


@router.message(DocumentStates.waiting_for_document, F.document)
@allowed_users_only
async def handle_document(message: Message, state: FSMContext):
    document = message.document
    if not document or not re.match(r"^\d{2}_\d{2}_\d{4}", document.file_name):
        await message.reply("Пожалуйста, отправьте правильный документ.")
        await state.clear()
        return

    file = await message.bot.get_file(document.file_id)
    file_path = os.path.join(DOCUMENTS_TO_SEND, document.file_name)
    await message.bot.download_file(file.file_path, file_path)

    await message.reply(f"Документ '{document.file_name}' успешно получен и сохранен.")
    await state.clear()


@router.message(DocumentStates.waiting_for_document)
async def handle_invalid_document(message: Message):
    await message.reply("Пожалуйста, отправьте документ.")


@router.message(Command("delete_documents"))
@allowed_users_only
async def delete_documents_command(message: Message):
    try:
        for filename in os.listdir(DOCUMENTS_TO_SEND):
            file_path = os.path.join(DOCUMENTS_TO_SEND, filename)
            os.remove(file_path)

        await message.reply("Все документы в папке для отправки были удалены.")
    except Exception as e:
        await message.reply(f"Произошла ошибка при удалении документов: {e}")


@router.message(Command(commands=["check_documents"]))
@allowed_users_only
async def check_documents_command(message: Message, state: FSMContext, bot: Bot):
    documents = os.listdir(DOCUMENTS_TO_SEND)
    if not documents:
        await message.answer(f"В папке {DOCUMENTS_TO_SEND} нет документов.")
    else:
        await message.answer(
            f"Отправляю вам все документы из папки {DOCUMENTS_TO_SEND}."
        )
        for file_name in documents:
            document_path = os.path.join(DOCUMENTS_TO_SEND, file_name)
            await bot.send_document(message.from_user.id, FSInputFile(document_path))


async def send_message_on_time(bot: Bot):
    sent = False
    try:
        send_message_to = load_send_to()
        date_string = datetime.now().strftime("%d_%m_%Y")
        documents = os.listdir(DOCUMENTS_TO_SEND)
        for user_id in send_message_to:
            for file_name in documents:
                document_path = os.path.join(DOCUMENTS_TO_SEND, file_name)
                if file_name.startswith(date_string):
                    sent = True
                    await bot.send_document(user_id, FSInputFile(document_path))
    except Exception as e:
        logger.error(e, exc_info=True)

    if sent:
        text = "Прошла рассылка опер. дежурного."
    else:
        text = "Никому ничего не отправилось."

    await bot.send_message(chat_id=322077458, text=text)


async def send_intro_message(bot: Bot, session: AsyncSession):
    async with session() as current_session:
        db = Database(session=current_session)

    text = random.choice(INTRO_MESSAGES)
    result = await db.get_chat_ids()
    tasks = [bot.send_message(chat_id=chat_id, text=text) for chat_id in result]
    await asyncio.gather(*tasks)
    await bot.send_message(
        chat_id=322077458, text=f"Прошла рассылка сообщения:\n\n{text}"
    )


async def ask_for_rating(bot: Bot, session: AsyncSession):
    from keyboards.keyboards_outer import inline_rating_keyboard

    async with session() as current_session:
        db = Database(session=current_session)

    text = "Пожалуйста, оцените нашу деятельность по шкале от 1 до 10."
    result = await db.get_chat_ids()
    tasks = [
        bot.send_message(
            chat_id=chat_id, text=text, reply_markup=inline_rating_keyboard()
        )
        for chat_id in result
    ]
    await asyncio.gather(*tasks)
    await bot.send_message(
        chat_id=322077458, text=f"Прошла рассылка сообщения:\n\n{text}"
    )


@router.callback_query(DialogCalendarCallback.filter())
async def process_dialog_calendar(
    callback_query: CallbackQuery, callback_data: CallbackData
):
    selected, date = await DialogCalendar().process_selection(
        callback_query, callback_data
    )
    if selected:
        date_string = date.strftime("%d_%m_%Y")

        documents = os.listdir(DOCUMENTS_TO_SEND)

        sent = False

        for file_name in documents:
            document_path = os.path.join(DOCUMENTS_TO_SEND, file_name)
            if file_name.startswith(date_string):
                sent = True
                await callback_query.message.answer_document(FSInputFile(document_path))
        if not sent:
            await callback_query.message.answer("Нет отчетов на выбранную дату")


@router.message(Command("send_news"))
@allowed_users_only
async def send_news_command(message: Message, state: FSMContext):
    try:
        document = message.document

        facts, world, conferences = await extract_news_from_document(
            document, message.bot
        )

        facts, world, conferences = (
            return_news_summary(
                [
                    document,
                ],
            )
            for document in (facts, world, conferences)
        )

        text = f"В России:\n\n{facts}\n\nВ мире:\n\n{world}\n\nКонференции:\n\n{conferences}"

        doc = Document()
        doc.add_paragraph(text)
        doc.save(f"/app/bot/tmp/{message.from_user.id}.docx")
        await message.answer_document(
            FSInputFile(
                f"/app/bot/tmp/{message.from_user.id}.docx", filename="Суммаризация.docx"
            )
        )
        await state.clear()
    except Exception as e:
        await message.bot.send_message(chat_id=322077458, text=str(e), parse_mode=None)
    finally:
        clear_temp(message.from_user.id)
