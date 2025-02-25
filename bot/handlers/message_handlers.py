import asyncio
import logging
import os
import random
from functools import wraps

from database import Database
from config_data.config import token, db_url
from dotenv import find_dotenv, load_dotenv
from keyboards.keyboards import inline_rating_keyboard
from lexicon.lexicon import INTRO_MESSAGES, LEXICON_COMMANDS_RU, LEXICON_RU
from services.log_actions import allowed_actions, log_action
from sqlalchemy.ext.asyncio import AsyncSession
from vkbottle import BaseStateGroup, DocMessagesUploader, PhotoMessageUploader
from vkbottle.bot import Bot, Message, MessageEvent
from vkbottle_types.events import GroupEventType
from vkbottle.bot import BotLabeler
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from services.rag import llm, get_context_str, text_qa_template
from services.prompt_templates import QUERY_GEN_PROMPT


class DocumentStates(BaseStateGroup):
    waiting_for_text = 0
    waiting_for_rating = 1
    waiting_for_feedback = 2


bot = Bot(token)

engine = create_async_engine(url=db_url, echo=True) 
session = async_sessionmaker(engine, expire_on_commit=False)

logger = logging.getLogger(__name__)

labeler = BotLabeler()

load_dotenv(find_dotenv())
mode = "outer"

send_message_from = list(map(int, os.getenv("SEND_MESSAGE_FROM").split(",")))


def allowed_users_only(func):
    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        if message.from_id not in send_message_from:
            await message.answer("У вас нет прав для использования этой команды.")
            return
        return await func(message, *args, **kwargs)
    return wrapper



@labeler.message(command="statistics")
@allowed_users_only
async def statistics(message: Message):
    doc_uploader = DocMessagesUploader(bot.api)
    doc = await doc_uploader.upload(
        file_source="/app/logs/stats.csv",
        peer_id=message.peer_id,
    )
    await message.answer(attachment=doc)


@labeler.message(command='send_to_everyone')
@allowed_users_only
async def process_send_command(message: Message):
    await message.reply("Пожалуйста, напишите текст для рассылки всем пользователям.")
    await message.state_dispenser.set(message.peer_id, DocumentStates.waiting_for_text)


@labeler.message(text="Обратная связь")
@allowed_users_only
async def get_feedback(message: Message):
    log_action(message, allowed_actions["menu"])
    answer_text, reply_markup, files = LEXICON_RU[message.text]
    await message.answer(answer_text, reply_markup=reply_markup)
    await message.state_dispenser.set(message.peer_id, DocumentStates.waiting_for_feedback)


@labeler.message(state=DocumentStates.waiting_for_feedback)
@allowed_users_only
async def process_feedback(message: Message):
    message_to_send = f"Поступила обратная связь от пользователя (chat id: {message.peer_id})\n\n{message.text}"

    for user in ["200820242",]:
        try:
            await message.ctx_api.messages.send(peer_id=user, message=message_to_send, random_id=random.randint(1, 1e6))
        except Exception:
            pass

    await message.reply("Спасибо за обратную связь, я передал её разработчикам.")
    await message.state_dispenser.delete(message.peer_id)


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


async def send_intro_message(message: Message):

    async with session() as current_session:
        db = Database(session=current_session)


    text = random.choice(INTRO_MESSAGES)
    result = await db.get_chat_ids()
    tasks = [message.ctx_api.messages.send(peer_id=chat_id, message=text, random_id=random.randint(1, 1e6)) for chat_id in result]
    await asyncio.gather(*tasks)
    await message.ctx_api.messages.send(peer_id=322077458, message=f'Прошла рассылка сообщения:\n\n{text}', random_id=random.randint(1, 1e6))


async def ask_for_rating(message: Message):

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
async def process_start_command(message: Message):


    async with session() as current_session:
        db = Database(session=current_session)

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
async def send(message: Message):

    text = message.text

    doc_uploader = PhotoMessageUploader(bot.api)
    if text in LEXICON_RU:
        log_action(message, allowed_actions['menu'])
        answer_text, reply_markup, files = LEXICON_RU[message.text]

        await message.answer(message=answer_text, keyboard=reply_markup)
        if files:
            for file in files:
                doc = await doc_uploader.upload(
                    file_source=file,
                    peer_id=message.peer_id,
                )
                await message.answer(attachment=doc)
        else:
            if text is None:
                return
    else:
        log_action(message, allowed_actions['ai'])
        try:
            query = await llm.ainvoke(QUERY_GEN_PROMPT.format(query=text))
#            await message.answer(query.content)
#            await message.ctx_api.messages.send(peer_id=200820242, text=text, random_id=random.randint(1, 1e6))
#            await message.ctx_api.messages.send(peer_id=200820242, text=query.content, random_id=random.randint(1, 1e6))
            context_str = await get_context_str(query.content)
#            await message.ctx_api.messages.send(peer_id=200820242, text=context_str, random_id=random.randint(1, 1e6))
#            try:
#                await message.answer(context_str)
#            except:
#                pass
            prompt = text_qa_template.format(context_str=context_str, query_str=text)
            chain = await llm.ainvoke(prompt)
            answer = chain.content
            logger.info(f'Пользователь {message.from_id} задал вопрос: "{text}", получен ответ: "{answer}"')
            await message.answer(answer)
        except Exception as e:
            error_text = f'Пользователь {message.from_id} получил ошибку\n{e}'
            logger.error(error_text, exc_info=True)
            await bot.api.messages.send(peer_id=200820242, message=error_text, random_id=random.randint(1, 1e6))
            await message.answer("Произошла ошибка при обработке Вашего запроса :(")
