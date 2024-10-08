import asyncio
import logging
import os
import random
from functools import wraps

from database import Database
from dotenv import find_dotenv, load_dotenv
from keyboards.keyboards import inline_rating_keyboard
from lexicon.lexicon import INTRO_MESSAGES, LEXICON_COMMANDS_RU, LEXICON_RU
from services.log_actions import allowed_actions, log_action
from services.rag import query_engine
from sqlalchemy.ext.asyncio import AsyncSession
from vkbottle import BaseStateGroup, DocMessagesUploader, PhotoMessageUploader
from vkbottle.bot import Bot, Message, MessageEvent
from vkbottle_types.events import GroupEventType
from vkbottle.bot import BotLabeler


class DocumentStates(BaseStateGroup):
    waiting_for_text = 0
    waiting_for_rating = 1


logger = logging.getLogger(__name__)

labeler = BotLabeler()


@labeler.message(text="test")
async def hi_handler(message: Message):
    await message.answer("Привет")


load_dotenv(find_dotenv())
mode = "outer"

send_message_from = list(map(int, os.getenv("SEND_MESSAGE_FROM").split(",")))


def allowed_users_only(func):
    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        if message.peer_id not in send_message_from:
            await message.answer("У вас нет прав для использования этой команды.")
            return
        return await func(message, *args, **kwargs)
    return wrapper



@labeler.message(command="help")
@allowed_users_only
async def help_command(message):
    help_text = """
Доступные команды:
/help - Показать список доступных команд
/send_document - Отправить новый документ
/delete_documents - Удалить все документы из папки для отправки
/check_documents - Проверить список документов в папке для отправки
/subscribe - Добавить себя в список рассылки (требуется пароль)
/send_to_everyone - Отправить всем сообщение
    """
    await message.answer(help_text)


@labeler.message(command="statistics")
@allowed_users_only
async def statistics(message: Message, bot: Bot):
    photo_uploader = PhotoMessageUploader(bot.api)
    doc = photo_uploader.upload(
        file_source="/app/logs/stats.csv",
        peer_id=message.peer_id,
    )
    await message.answer(attachment=doc)


@labeler.message(command='send_to_everyone')
@allowed_users_only
async def process_send_command(message: Message):
    await message.reply("Пожалуйста, напишите текст для рассылки всем пользователям.")
    await message.state_dispenser.set(message.peer_id, DocumentStates.waiting_for_text)


@labeler.message(state=DocumentStates.waiting_for_text)
async def send_to_everyone(message: Message, db: Database):
    if message.text:
        result = await db.get_chat_ids()
        tasks = [message.ctx_api.messages.send(peer_id=chat_id, message=message.text, random_id=random.randint(1, 1e6)) for chat_id in result]
        await asyncio.gather(*tasks)
        await message.reply("Рассылка прошла успешно.")
    else:
        await message.reply("Нет текста.")
    await message.state_dispenser.delete(message.peer_id)


async def send_intro_message(message: Message, session: AsyncSession):

    async with session() as current_session:
        db = Database(session=current_session)

    text = random.choice(INTRO_MESSAGES)
    result = await db.get_chat_ids()
    tasks = [message.ctx_api.messages.send(peer_id=chat_id, message=text, random_id=random.randint(1, 1e6)) for chat_id in result]
    await asyncio.gather(*tasks)
    await message.ctx_api.messages.send(peer_id=322077458, message=f'Прошла рассылка сообщения:\n\n{text}', random_id=random.randint(1, 1e6))


async def ask_for_rating(message: Message, session: AsyncSession):

    async with session() as current_session:
        db = Database(session=current_session)

    text = "Пожалуйста, оцените нашу деятельность по шкале от 1 до 10."
    result = await db.get_chat_ids()
    tasks = [message.ctx_api.messages.send(peer_id=chat_id, message=text, keyboard=inline_rating_keyboard(), random_id=random.randint(1, 1e6)) for chat_id in result]
    await asyncio.gather(*tasks)
    await message.ctx_api.messages.send(peer_id=322077458, message=f'Прошла рассылка сообщения:\n\n{text}', random_id=random.randint(1, 1e6))


@labeler.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent)
async def process_rating(event: MessageEvent, bot: Bot):
    await event.show_snackbar("Спасибо за Вашу оценку!")
    rating = event.payload['rating']
    await bot.api.messages.delete(peer_id=event.peer_id, message_ids=[event.message_id], delete_for_all=True)
    logger.info(f'Поставлена оценка {rating}')



@labeler.message(command='start')
async def process_start_command(message: Message, db: Database):
    try:
        log_action(message, allowed_actions['start'])
    except Exception as e:
        logger.error(e, exc_info=True)
    logger.info(f'Пользователь {message.from_id} начал диалог, код чата {message.peer_id}')
    answer_text, reply_markup, files = LEXICON_COMMANDS_RU['/start']
    await message.answer(answer_text, keyboard=reply_markup)
    await db.add_user(
        id=message.peer_id,
    )


@labeler.message()
async def send(message: Message, bot: Bot):

    doc_uploader = DocMessagesUploader(bot.api)
    if message.text in LEXICON_RU:
        log_action(message, allowed_actions['menu'])
        answer_text, reply_markup, files = LEXICON_RU[message.text]

        await message.answer(message=answer_text, keyboard=reply_markup)
        if files:
            for file in files:
                doc = doc_uploader.upload(
                    file_source=file.split('/')[-1],
                    peer_id=message.peer_id,
                )
                await message.answer(attachment=doc)
        else:
            text = message.text
            if text is None:
                return

        try:
            chain = await query_engine.aquery(text)
            answer = chain.__str__()
            logger.info(f'Пользователь {message.from_user.username} задал вопрос: "{text}", получен ответ: "{answer}"')
            await message.answer(answer)
        except Exception as e:
            error_text = f'Пользователь {message.from_id} получил ошибку\n{e}'
            logger.error(error_text, exc_info=True)
            await bot.api.messages.send(peer_id=322077458, message=error_text, random_id=random.randint(1, 1e6))
            await message.answer("Произошла ошибка при обработке Вашего запроса :(")

