from aiogram import Router
from aiogram.types import Message
import logging
from pyrogram import Client
from pyrogram.types import Message
from pathlib import Path

from services.converter import clear_temp, convert, recognize, is_audio, is_video
from services.summarization import get_summary


router = Router()

logger = logging.getLogger(__name__)


async def send_protocol(app: Client, message: Message):

    await message.reply("Медиафайл получен, готовится транскрипция...")

    if message.video:
        file_id = message.video.file_id
    elif message.audio:
        file_id = message.audio.file_id
    elif message.voice:
        file_id = message.voice.file_id
    else:
        file_id = message.document.file_id

    try:
        file_path = await message.download(file_name='./tmp/')
        file_id = Path(file_path).stem
        extension = file_path.split('.')[-1]
        audio_destination = f'./tmp/{file_id}.wav'

        if message.video or is_video(extension):
            convert(file_path, audio_destination)
            extension = 'wav'
        elif message.voice or message.audio or is_audio(extension):
            pass
        else:
            await message.reply("Не распознан формат файла")
            await app.send_message(322077458, f"Не распознан формат {extension}")
            return

        document, file_name, text = await recognize(file_id, extension)
        await message.reply_document(document=document, file_name=file_name)
        document_sum, file_name_sum = await get_summary(file_id, text)
        await message.reply_document(document=document_sum, file_name=file_name_sum)
        logger.info(f'Пользователь {message.from_user.username} отправил файл формата {extension} и получил ответ.')

    except Exception as e:
        error_text = f'Пользователь {message.from_user.username} отправил файл формата {extension} и получил ошибку\n{e}'
        logger.error(error_text, exc_info=True)
        await message.reply("Произошла ошибка при обработке Вашего файла\nИнформация отправлена разработчикам")
        await app.send_message(322077458, error_text)

    finally:
        clear_temp(file_id)