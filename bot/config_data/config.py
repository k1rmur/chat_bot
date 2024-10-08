from environs import Env
from vkbottle import BuiltinStateDispenser

env = Env()
env.read_env()
token=env('BOT_TOKEN')
db_url=env('DB_URL')

state_dispenser = BuiltinStateDispenser()
