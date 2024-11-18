import asyncio
import logging
import logging.config
import os
from datetime import timedelta, timezone
from optparse import OptionParser

import services.initialize_db_name as db
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config_data.config import Config, load_config
from database import Base
from dotenv import find_dotenv, load_dotenv
from handlers import video_protocols, docsummary
from logging_settings import logging_config
from middlewares import DatabaseMiddleware
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

load_dotenv(find_dotenv())
mode = os.getenv("MODE")


parser = OptionParser()
parser.add_option('--Mode', type=str, default="inner")

db.initialize_db(mode)
from handlers import send_documents, user_handlers

logging.config.dictConfig(logging_config)
config: Config = load_config()


async def main():

    engine = create_async_engine(url=config.db_url, echo=True)
    session = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    dp.include_router(send_documents.router)

    scheduler = AsyncIOScheduler()

    if mode == 'inner':
        app = Client(
            "DA_bot_test",
            api_id=config.tg_bot.api_id, api_hash=config.tg_bot.api_hash,
            bot_token=config.tg_bot.token
        )
        app.add_handler(MessageHandler(video_protocols.send_protocol, filters=filters.video | filters.voice | filters.audio | filters.document))
        await app.start()
        scheduler.add_job(send_documents.send_message_on_time, "cron", hour=10, minute=00, timezone=timezone(timedelta(hours=+3)), args=(bot,))
        dp.include_router(docsummary.router)
    else:
        scheduler.add_job(send_documents.ask_for_rating, "cron", day='2nd fri, 3rd wed', hour=16, minute=30, timezone=timezone(timedelta(hours=+3)), args=(bot, session))


    scheduler.add_job(send_documents.send_intro_message, "cron", day='2nd fri, 3rd wed', hour=16, minute=30, timezone=timezone(timedelta(hours=+3)), args=(bot, session))
    scheduler.start()

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
