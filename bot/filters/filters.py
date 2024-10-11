from aiogram.types import Message, ChatMemberAdministrator, ChatMemberMember, ChatMemberOwner
from functools import wraps
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

send_message_from = list(map(int, os.getenv("SEND_MESSAGE_FROM").split(","))) 


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
