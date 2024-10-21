import asyncio
import logging
import logging.config
import os
from datetime import timedelta, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config_data.config import state_dispenser, token
from handlers import message_handlers
from vkbottle import Bot
from handlers import labelers

mode = "outer"

#logging.config.dictConfig(logging_config)

bot = Bot(
    token=token,
    state_dispenser=state_dispenser,
)

for custom_labeler in labelers:
    bot.labeler.load(custom_labeler)


async def main():

    scheduler = AsyncIOScheduler()

    scheduler.add_job(message_handlers.ask_for_rating, "cron", day='1st wed, 3rd wed', hour=19, minute=00, timezone=timezone(timedelta(hours=+3)), args=(bot,))
    scheduler.add_job(message_handlers.send_intro_message, "cron", day='1st wed, 3rd wed', hour=19, minute=00, timezone=timezone(timedelta(hours=+3)), args=(bot,))

    scheduler.start()


if __name__ == '__main__':
    if not os.path.exists("./tmp"):
        os.mkdir("./tmp")
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    bot.loop_wrapper.add_task(bot.run_polling())
    bot.loop_wrapper.add_task(main())
    bot.loop_wrapper.run()
