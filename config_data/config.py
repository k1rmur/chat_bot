from dataclasses import dataclass
from environs import Env


@dataclass
#class DatabaseConfig:
#    database: str         # Название базы данных
#    db_host: str          # URL-адрес базы данных
#    db_user: str          # Username пользователя базы данных
#    db_password: str      # Пароль к базе данных


@dataclass
class TgBot:
    token: str            # Токен для доступа к телеграм-боту
#    admin_ids: list[int]  # Список id администраторов бота


@dataclass
class Config:
    tg_bot: TgBot
#    db: DatabaseConfig


def load_config(path: str | None = None, mode: str = 'inner') -> Config:
    env = Env()
    env.read_env(path)
    if mode == 'inner':
        token = env('BOT_TOKEN_INNER')
    else:
        token = env('BOT_TOKEN_OUTER')
    return Config(tg_bot=TgBot(token=token))