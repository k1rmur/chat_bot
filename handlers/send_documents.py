from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import Command
from functools import wraps
import os
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile
import logging


DOCUMENTS_TO_SEND = "/app/documents_to_send"
DOCUMENTS_SENT = "/app/documents_sent"

logger = logging.getLogger(__name__)


router = Router()

send_message_to = list(map(int, os.getenv("SEND_MESSAGE_TO").split(","))) 
send_message_from = list(map(int, os.getenv("SEND_MESSAGE_FROM").split(","))) 


def allowed_users_only(func):
    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        if message.from_user.id not in send_message_from:
            await message.reply("У вас нет прав для использования этой команды.")
            return
        return await func(message, *args, **kwargs)
    return wrapper


class DocumentStates(StatesGroup):
    waiting_for_document = State()


@router.message(Command("help"))
@allowed_users_only
async def help_command(message: Message):
    help_text = """
Доступные команды:
/help - Показать список доступных команд
/send_document - Отправить новый документ
/delete_documents - Удалить все документы из папки для отправки
/check_documents - Проверить список документов в папке для отправки
    """
    await message.reply(help_text)


@router.message(Command("send_document"))
@allowed_users_only
async def send_document_command(message: Message, state: FSMContext):
    if len(os.listdir(DOCUMENTS_TO_SEND)) != 0:
        await message.reply("Файл уже добавлен.")
        return

    await message.reply("Пожалуйста, отправьте документ.")
    await state.set_state(DocumentStates.waiting_for_document)


@router.message(DocumentStates.waiting_for_document, F.document)
@allowed_users_only
async def handle_document(message: Message, state: FSMContext):

    document = message.document
    if not document:
        await message.reply("Пожалуйста, отправьте документ.")
        return

    # Скачиваем документ в память
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


@router.message(Command(commands=['check_documents']))
@allowed_users_only
async def check_documents_command(message: Message, state: FSMContext, bot: Bot):
    documents = os.listdir(DOCUMENTS_TO_SEND)
    if not documents:
        await message.answer(f"В папке {DOCUMENTS_TO_SEND} нет документов.")
    else:
        await message.answer(f"Отправляю вам все документы из папки {DOCUMENTS_TO_SEND}.")
        for file_name in documents:
            document_path = os.path.join(DOCUMENTS_TO_SEND, file_name)
            await bot.send_document(message.from_user.id, FSInputFile(document_path))



async def send_message_on_time(bot: Bot):
    for filename in os.listdir(DOCUMENTS_TO_SEND):
        file_path = os.path.join(DOCUMENTS_TO_SEND, filename)
        for user_id in send_message_to:
            try:
                await bot.send_document(user_id, FSInputFile(file_path))
            except Exception as e:
                logger.error(e, exc_info=True)
        os.rename(file_path, os.path.join(DOCUMENTS_SENT, filename))