import logging
import os
from pathlib import Path

import aiohttp
from aiogram import Router
from dotenv import find_dotenv, load_dotenv
from pyrogram import Client
from pyrogram.types import ChatMember, Message
from services.converter import clear_temp, convert, is_audio, is_video, salute_recognize
from services.summarization import get_summary


class NoWordsRecognizedError(Exception):
    pass


router = Router()

logger = logging.getLogger(__name__)


load_dotenv(find_dotenv())


async def download_file(message: Message):
    message_to_delete = await message.reply("Скачивание медиафайла...")
    file_path = await message.download(file_name="./tmp/")
    extension = file_path.split(".")[-1]
    os.rename(file_path, f"./tmp/{message.id}.{extension}")
    file_path = f"./tmp/{message.id}.{extension}"
    await message_to_delete.delete()
    file_id = Path(file_path).stem
    if not is_audio(extension) and not is_video(extension) and extension != "txt":
        return

    return {"file_path": file_path, "file_id": file_id, "extension": extension}


async def recognize_from_audio(
    file_id: str,
    extension: str,
    message_to_delete: Message,
    message: Message,
):
    document, file_name, text = salute_recognize(file_id, extension)
    if len(text.strip()) < 10:
        await message_to_delete.delete()
        await message.reply("Слова в медиафайле не распознаны.")
        raise NoWordsRecognizedError(
            f"Пользователю (username={message.from_user.username} id={message.from_user.id}) не пришла транскрипция, не распознаны слова."
        )

    await message_to_delete.delete()
    await message.reply_document(document=document, file_name=file_name)
    logger.info(
        f"Пользователю (username={message.from_user.username} id={message.from_user.id}) пришла транскрипция."
    )

    return text


async def get_protocol(app: Client, message: Message, file_id: str, text: str):
    message_to_delete = await message.reply("Готовится протокол совещания...")
    document_sum, file_name_sum = await get_summary(file_id, text, message)

    await message_to_delete.delete()
    await message.reply_document(document=document_sum, file_name=file_name_sum)

    logger.info(
        f"Пользователь (username={message.from_user.username} id={message.from_user.id}) получил протокол."
    )
    try:
        await app.send_document(
            chat_id="-1002240095685",
            document=document_sum,
            file_name=file_name_sum,
            caption=f"@{message.from_user.username}",
        )
    except:
        pass


async def get_protocol_from_txt(
    file_path: str, file_id: str, message: Message, app: Client
):
    with open(file_path, "r") as file:
        text = file.read()

    await get_protocol(app, message, file_id, text)


async def send_protocol(app: Client, message: Message):
    try:
        user_status = await app.get_chat_member(
            chat_id="-1002409517684", user_id=message.from_user.id
        )
    except Exception as e:
        await message.reply("Нужно написать /start в беседу цифровизаторов.")
    if not isinstance(
        user_status,
        (ChatMember),
    ):
        await message.reply("У вас нет прав для использования этого бота.")
        return

    result = await download_file(message)
    if result is None:
        return
    else:
        file_id = result.get("file_id")
        extension = result.get("extension")
        file_path = result.get("file_path")

    logger.info(
        f"Пользователь (username={message.from_user.username} id={message.from_user.id}) отправил файл {file_id}"
    )
    message_to_delete = await message.reply(
        "Медиафайл получен, готовится расшифровка текста..."
    )

    try:
        audio_destination = f"/app/bot/tmp/{file_id}.wav"
        if message.video or is_video(extension):
            convert(file_path, audio_destination)
            extension = "wav"
        elif message.voice or message.audio or is_audio(extension):
            pass
        elif extension == "txt":
            message_to_delete.delete()
            await get_protocol_from_txt(file_path, file_id, message, app)
            return
        else:
            return

        text = await recognize_from_audio(
            file_id, extension, message_to_delete, message
        )

        await get_protocol(app, message, file_id, text)

    except Exception as e:
        error_text = f"Пользователь {message.from_user.username} отправил файл формата {extension} и получил ошибку\n{e}"
        logger.error(error_text, exc_info=True)
        await message.reply(
            "Произошла ошибка при обработке Вашего файла\nИнформация отправлена разработчикам"
        )
        await app.send_message(322077458, error_text)

    finally:
        clear_temp(file_id)


async def make_protocol_from_url(app: Client, message: Message):
    """
    Function for URL handling.
    Checks if text is a valid URL string, then checks if text is a link to video.
    If it is, downloads a video in storage.
    """

    try:
        url = message.text.strip()
        async with aiohttp.ClientSession() as video_session:
            async with video_session.get(url) as response:
                if response.status != 200:
                    await message.reply(
                        "Не удалось получить доступ к видео по предоставленной ссылке."
                    )
                    return

                for key in response.headers:
                    await message.reply(f"{key}: {response.headers[key]}")
                content_type = response.headers.get("Content-Type", "")
                if "video" not in content_type:
                    await message.reply("Ссылка не ведет на видеофайл.")
                    return

                file_path = f"./tmp/{Path(url).name}"
                with open(file_path, "wb") as f:
                    f.write(await response.read())

        message_to_delete = await message.reply("Видео успешно загружено.")
        logger.info(
            f"Пользователь (username={message.from_user.username} id={message.from_user.id}) загрузил видео из URL {url}"
        )
        file_id = Path(file_path).stem
        audio_destination = f"/app/bot/tmp/{file_id}.wav"
        convert(file_path, audio_destination)

        text = await recognize_from_audio(
            file_id,
            "wav",
            message_to_delete,
            message,
        )

        await get_protocol(app, message, file_id, text)

    except Exception as e:
        error_text = f"Пользователь {message.from_user.username} отправил URL {url} и получил ошибку\n{e}"
        logger.error(error_text, exc_info=True)
        await message.reply(
            "Произошла ошибка при обработке Вашего файла\nИнформация отправлена разработчикам"
        )
        await app.send_message(322077458, error_text)

    finally:
        clear_temp(file_id)
