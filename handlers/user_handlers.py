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
from services.converter import recognize, clear_temp

load_dotenv(find_dotenv())
mode = os.getenv("MODE")
print(mode)

if mode == 'inner':
    from lexicon.lexicon_inner import LEXICON_RU, LEXICON_COMMANDS_RU
else:
    from lexicon.lexicon_outer import LEXICON_RU, LEXICON_COMMANDS_RU


send_message_to = list(map(int, os.getenv("SEND_MESSAGE_TO").split(","))) 
router = Router()

logger = logging.getLogger(__name__)

@router.message(CommandStart())
async def process_start_command(message: Message):
    logger.info(f'Пользователь {message.from_user.username} начал диалог, код чата {message.chat.id}')
    answer_text, reply_markup = LEXICON_COMMANDS_RU['/start']
    await message.answer(answer_text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)


@router.message(Command(commands=["clear"]))
async def process_clear_command(message: Message):
    user_id = message.from_user.id
    conversation_history[user_id] = ChatMessageHistory()
    logger.info(f'Пользователь {message.from_user.username} очистил историю диалога')
    await message.answer(text=LEXICON_RU['/clear'])


@router.message((F.text | F.voice) & ~F.text.startswith('/'))
async def send(message: Message, bot: Bot):
    if message.text in LEXICON_RU:
        answer_text, reply_markup = LEXICON_RU[message.text]
        await message.answer(text=answer_text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    else:
        session_id = message.from_user.id
        if message.voice:
            try:
                file_id = message.voice.file_id
                file = await bot.get_file(file_id=file_id)
                file_path = file.file_path
                audio_destination = f'./tmp/{file_id}.wav'
                await bot.download_file(file_path, audio_destination)
                text = await recognize(file_id)
                clear_temp()
            except Exception as e:
                await message.reply("Произошла ошибка при распознавании голосового сообщения :(")
                logger.error(e, exc_info=True)
                clear_temp()
                return
        else:
            text = message.text

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
