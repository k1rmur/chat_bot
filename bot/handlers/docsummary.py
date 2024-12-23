import logging
import traceback

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile, Message
from config_data.config import Config, load_config
from docx import Document
from dotenv import find_dotenv, load_dotenv
from filters.filters import users_from_group_only
from services.map_reduce_docs import clear_temp, return_summary
from services.text_extraction import extract_text_from_document

router = Router()
config: Config = load_config()


class SummaryStates(StatesGroup):
    waiting_for_document_summary = State()


load_dotenv(find_dotenv())

logger = logging.getLogger(__name__)


@router.message(Command("summarize_documents"))
@users_from_group_only
async def send_document_command(message: Message, state: FSMContext):
    await message.reply(
        "Пожалуйста, отправьте один или несколько документов. Отправьте /process, чтобы начать их обработку."
    )
    await state.set_state(SummaryStates.waiting_for_document_summary)


@router.message(Command("clear"))
@users_from_group_only
async def clear_command(message: Message, state: FSMContext):
    await message.reply("Очищено.")
    await state.clear()


@router.message(SummaryStates.waiting_for_document_summary, F.document)
async def document_handler(message: Message, state: FSMContext):
    document = message.document

    langchain_document = await extract_text_from_document(document, message.bot)

    try:
        data = await state.get_data()

        if "langchain_documents" not in data:
            data["langchain_documents"] = []
        data["langchain_documents"].append(langchain_document)

        await state.set_data(data)

    except Exception as e:
        await message.reply(str(e))

    await message.answer(
        f"Текст из документа '{document.file_name}' сохранен. Отправьте еще документы или /process для обработки."
    )


@router.message(SummaryStates.waiting_for_document_summary, Command("process"))
async def text_message_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    documents = data.get("langchain_documents", dict())
    try:
        await message.answer(
            f"Началась обработка, количество документов - {len(documents)}..."
        )
        summarized_text = return_summary(documents)
    except Exception as e:
        tb = traceback.format_exc()
        with open("/app/logs/error.txt", "w") as file:
            file.write(tb)

    doc = Document()
    doc.add_paragraph(summarized_text)
    doc.save(f"./tmp/{message.from_user.id}.docx")
    await message.answer_document(
        FSInputFile(f"./tmp/{message.from_user.id}.docx", filename="Суммаризация.docx")
    )
    await state.clear()

    clear_temp(message.from_user.id)
