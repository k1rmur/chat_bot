import logging
import os

import docx
import langchain_core.documents
from aiogram import Bot
from aiogram.types import Document


logger = logging.getLogger(__name__)


async def extract_text_from_document(document: Document, bot: Bot):
    """
    Функция, переводящая объект Document aiogram (который содержит docx файл) в Document Langchain
    """
    # Получаем файл с серверов Telegram

    file_info = await bot.get_file(document.file_id)
    file_path = file_info.file_path

    # Загружаем файл на локальный диск
    downloaded_file = await bot.download_file(file_path)

    # Временное имя файла
    temp_file_name = f"temp_{document.file_id}.docx"

    # Сохраняем документ на диск
    with open(temp_file_name, "wb") as f:
        f.write(downloaded_file.getvalue())

    # Извлекаем текст из документа
    doc = docx.Document(temp_file_name)
    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)

    # Удаляем временный файл
    os.remove(temp_file_name)

    langchain_document = langchain_core.documents.Document(page_content="\n".join(full_text))

    return langchain_document
