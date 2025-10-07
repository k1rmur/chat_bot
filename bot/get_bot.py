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
from vkbottle import BaseStateGroup
from vkbottle.bot import Message
from services.log_actions import allowed_actions, log_action
from lexicon.lexicon import INTRO_MESSAGES, LEXICON_COMMANDS_RU, LEXICON_RU
import random


class FeedBackStates(BaseStateGroup):
    waiting_for_feedback = 0

mode = "outer"

bot = Bot(
    token=token,
    state_dispenser=state_dispenser,
)

@bot.on.message(text="Обратная связь")
async def get_feedback(message: Message):
    log_action(message, allowed_actions["menu"])
    answer_text, reply_markup, files = LEXICON_RU[message.text]
    await message.answer(answer_text, reply_markup=reply_markup)
    await bot.state_dispenser.set(message.peer_id, FeedBackStates.waiting_for_feedback)


@bot.on.message(state=FeedBackStates.waiting_for_feedback)
async def process_feedback(message: Message):
    await bot.state_dispenser.delete(message.peer_id)
    message_to_send = f"Поступила обратная связь от пользователя (chat id: {message.peer_id})\n\n{message.text}"

    for user in ["200820242",]:
        await message.ctx_api.messages.send(peer_id=user, message=message_to_send, random_id=random.randint(1, 1e6))

    await message.reply("Спасибо за обратную связь, я передал её разработчикам.")

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
