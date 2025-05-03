from aiogram import F, Router
from aiogram.types import CallbackQuery
from core import message_templates as mt

router = Router(name=__name__)


@router.callback_query(F.data == 'guide_android')
async def guide_android_query_handler(query: CallbackQuery):
    await query.answer()


@router.callback_query(F.data == 'guide_apple')
async def guide_apple_query_handler(query: CallbackQuery):
    await query.bot.send_(chat_id=query.from_user.id, text=mt.guide_apple)
    await query.answer()


@router.callback_query(F.data == 'guide_windows')
async def guide_windows_query_handler(query: CallbackQuery):
    await query.answer()
