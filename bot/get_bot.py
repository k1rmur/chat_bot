import asyncio
import logging
import logging.config
import os
from datetime import timedelta, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config_data.config import db_url, labeler, state_dispenser, token
from database import Base
from handlers import message_handlers
from logging_settings import logging_config
from middlewares import DatabaseMiddleware
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from vkbottle import Bot
from vkbottle.bot import Message

mode = "outer"

logging.config.dictConfig(logging_config)

bot = Bot(
    token=token,
#    labeler=labeler,
#    state_dispenser=state_dispenser,
)


@bot.on.private_message(text="test")
async def hi_handler(message: Message):
    users_info = await bot.api.users.get(message.from_id)
    await message.answer("Привет, {}".format(str(users_info)))


async def main():

    engine = create_async_engine(url=db_url, echo=True)
    session = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    scheduler = AsyncIOScheduler()

    scheduler.add_job(message_handlers.ask_for_rating, "cron", day='1st wed, 3rd wed', hour=19, minute=00, timezone=timezone(timedelta(hours=+3)), args=(bot, session))
    scheduler.add_job(message_handlers.send_intro_message, "cron", day='1st wed, 3rd wed', hour=19, minute=00, timezone=timezone(timedelta(hours=+3)), args=(bot, session))

    scheduler.start()
#    bot.labeler.message_view.register_middleware(DatabaseMiddleware)


if __name__ == '__main__':
    if not os.path.exists("./tmp"):
        os.mkdir("./tmp")
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    bot.loop_wrapper.add_task(bot.run_polling())
    bot.loop_wrapper.add_task(main())
    bot.loop_wrapper.run()
