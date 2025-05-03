import asyncio
from typing import Any

from aiogram.exceptions import TelegramRetryAfter

from core.config import env, logger_bot

lock = asyncio.Lock()


async def send_message_to_admins_chat(text: str) -> None:
    async with lock:
        try:
            await logger_bot.send_message(
                chat_id=env.TELEGRAM_LOGGING_CHAT_ID, text=text
            )
        except TelegramRetryAfter as _ex:
            await asyncio.sleep(_ex.retry_after + 1)
            await logger_bot.send_message(
                chat_id=env.TELEGRAM_LOGGING_CHAT_ID, text=text
            )


async def log_to_telegram_bot(
    log: Any | str, msg_length_limit: int = 4096
) -> None:
    """
    sink for loguru
    """

    log_length = len(log)
    if log_length > msg_length_limit:
        messages = (
            log[i : i + msg_length_limit]
            for i in range(log_length, msg_length_limit)
        )
        for message in messages:
            await send_message_to_admins_chat(message)
    else:
        await send_message_to_admins_chat(log)
