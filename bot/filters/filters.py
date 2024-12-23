import os
from functools import wraps
from typing import Union

import pyrogram.types as types
from aiogram.filters import BaseFilter
from aiogram.types import (
    ChatMemberAdministrator,
    ChatMemberMember,
    ChatMemberOwner,
    Message,
)
from dotenv import find_dotenv, load_dotenv
from pyrogram import Client, filters
from validators import url

load_dotenv(find_dotenv())

send_message_from = list(map(int, os.getenv("SEND_MESSAGE_FROM").split(",")))


async def url_func(_, __, message):
    """
    Function that checks if message text is a valid URL
    """
    return url(message.text)


url_filter = filters.create(url_func)


def users_from_group_only(func):
    """
    Wrapper for access restriction to only those who are members of a particular group
    """

    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        user_status = await message.bot.get_chat_member(
            chat_id="-1002409517684", user_id=message.from_user.id
        )
        print(user_status)
        if not isinstance(
            user_status,
            (
                ChatMemberOwner,
                ChatMemberAdministrator,
                ChatMemberMember,
            ),
        ):
            await message.reply("У вас нет прав для использования этого бота.")
            return
        return await func(message, *args, **kwargs)

    return wrapper


def allowed_users_only(func):
    """
    Wrapper for access restriction to only those who are in some list
    """

    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        if message.from_user.id not in send_message_from:
            await message.reply("У вас нет прав для использования этой команды.")
            return
        return await func(message, *args, **kwargs)

    return wrapper


class ChatTypeFilter(BaseFilter):
    def __init__(self, chat_type: Union[str, list]):
        self.chat_type = chat_type

    async def __call__(self, message: Message) -> bool:
        if isinstance(self.chat_type, str):
            return message.chat.type == self.chat_type
        else:
            return message.chat.type in self.chat_type
