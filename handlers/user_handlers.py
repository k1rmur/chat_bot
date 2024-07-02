from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from lexicon.lexicon import LEXICON_RU
from langchain_community.chat_message_histories import ChatMessageHistory

from services.rag import conversation_history, conversational_rag_chain, MESSAGE_THRESHOLD


router = Router()



@router.message(CommandStart())
async def process_start_command(message: Message):
#    logger.info(f'Пользователь {message.from_user.username} начал диалог')
    await message.answer(text=LEXICON_RU['/start'])


@router.message(Command(commands=["clear"]))
async def process_clear_command(message: Message):
    user_id = message.from_user.id
    conversation_history[user_id] = ChatMessageHistory()
#    logger.info(f'Пользователь {message.from_user.username} очистил историю диалога')
    await message.answer(text=LEXICON_RU['/clear'])


@router.message(F.text)
async def send(message: Message):
    session_id = message.from_user.id
    try:
        answer = conversational_rag_chain.invoke(
            {"input": message.text},
            config={
                "configurable": {"session_id": session_id}
            }
        )["answer"]
        # Сохраняем только последние несколько вопросов-ответов, чтобы не забивать память
        conversation_history[session_id].messages = conversation_history[session_id].messages[-MESSAGE_THRESHOLD*2:]
#        logger.info(f'Пользователь {message.from_user.username} задал вопрос: "{message.text}", получен ответ: "{answer}"')
    except Exception as e:
        print(e)
#        logger.error(e, exc_info=True)

    await message.reply(text=answer)
