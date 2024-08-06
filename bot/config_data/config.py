from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str
    api_id: int
    api_hash: str


@dataclass
class Config:
    tg_bot: TgBot
    db_url: str


def load_config(path: str | None = None, mode: str = 'inner') -> Config:
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(
        token=env('BOT_TOKEN'),
        api_id=env('API_ID'),
        api_hash=env('API_HASH'),
        ),
	    db_url=env('DB_URL')
    )
