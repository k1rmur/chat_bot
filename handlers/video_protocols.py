from aiogram import Router, F
from aiogram.types import Message
from aiogram import Bot
from services.converter import convert, recognize
import os
import glob

router = Router()


@router.message(F.video)
async def send_protocol(message: Message, bot: Bot):
    await message.reply("Видео получено, готовится транскрипция...")
    try:
        file_id = message.video.file_id
        file = await bot.get_file(file_id=file_id)
        file_path = file.file_path
        video_destination = f'./tmp/{file_id}.mp4'
        audio_destination = f'./tmp/{file_id}.wav'
        await bot.download_file(file_path, video_destination)
        convert(video_destination, audio_destination)
        input_file = recognize(file_id)
        await message.answer_document(input_file)

    except Exception as e:
        print(e)

    finally:
        files = glob.glob('./tmp/*')
        for f in files:
            print(f)
            os.remove(f)
