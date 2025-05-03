from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

import core.message_templates as mt
from keyboards import user_keyboard
from tools.functions import send_message_and_delete_previous

router = Router(name=__name__)


@router.message(CommandStart())
async def start_commmand_handler(msg: Message):
    return await send_message_and_delete_previous(
        chat_id=msg.from_user.id,
        text=mt.command_start,
        redis_key='start_message',
        reply_markup=user_keyboard,
    )
