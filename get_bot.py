import logging
import asyncio
import logging.config
from logging_settings import logging_config
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config_data.config import Config, load_config
from handlers import user_handlers, video_protocols
from keyboards.set_menu import set_main_menu


logger = logging.getLogger(__name__)


async def main():
    logging.config.dictConfig(logging_config)

    config: Config = load_config()

    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    await set_main_menu(bot)
    dp.include_router(user_handlers.router)
    dp.include_router(video_protocols.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    print("Бот запускается")
    asyncio.run(main())