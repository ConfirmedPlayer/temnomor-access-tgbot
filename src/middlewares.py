from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message


class PrivateChatsOnlyMiddleware(BaseMiddleware):
    async def __call__(
        self, handler, event: Message, data: dict[str, Any]
    ) -> Any:
        if event.chat.type == 'private':
            return await handler(event, data)
