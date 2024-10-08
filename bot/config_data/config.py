from environs import Env
from vkbottle import API, BuiltinStateDispenser
from vkbottle.bot import BotLabeler

env = Env()
env.read_env()
token=env('BOT_TOKEN')
db_url=env('DB_URL')

labeler = BotLabeler()
state_dispenser = BuiltinStateDispenser()
