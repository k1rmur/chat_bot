import logging
import asyncio
import logging.config
from logging_settings import logging_config
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config_data.config import Config, load_config
from optparse import OptionParser
import services.initialize_db_name as db
from handlers import video_protocols
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import timezone, timedelta
from dotenv import load_dotenv, find_dotenv
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from middlewares import DatabaseMiddleware


load_dotenv(find_dotenv())
mode = os.getenv("MODE")


parser = OptionParser()
parser.add_option('--Mode', type=str, default="inner")

db.initialize_db(mode)
from handlers import user_handlers, send_documents

logging.config.dictConfig(logging_config)
config: Config = load_config(mode=mode)


async def main():

    app = Client(
        "DA_bot_test",
        api_id=config.tg_bot.api_id, api_hash=config.tg_bot.api_hash,
        bot_token=config.tg_bot.token
    )
    engine = create_async_engine(url=config.db_url, echo=True)
    session = async_sessionmaker(engine, expire_on_commit=False)

    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    if mode == 'inner':
        app.add_handler(MessageHandler(video_protocols.send_protocol, filters=filters.video | filters.audio | filters.document))
        dp.include_router(send_documents.router)
        scheduler = AsyncIOScheduler()
        scheduler.add_job(send_documents.send_message_on_time, "cron", day_of_week='wed', hour=10, minute=00, timezone=timezone(timedelta(hours=+3)), args=(bot,))
        scheduler.start()
        await app.start()

    dp.include_router(user_handlers.router)
    dp.update.middleware(DatabaseMiddleware(session=session))

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.send_message(322077458, "Я запустился")
    await dp.start_polling(bot)


if __name__ == '__main__':
    print("Бот запускается")
    if not os.path.exists("./tmp"):
        os.mkdir("./tmp")
    if mode=='inner':
        if not os.path.exists("./documents_to_send"):
            os.mkdir("./documents_to_send")
        if not os.path.exists("./documents_sent"):
            os.mkdir("./documents_sent")
        if not os.path.exists("./send_to"):
            os.mkdir("./send_to")
    asyncio.run(main())
