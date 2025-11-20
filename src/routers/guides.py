from aiogram import F, Router
from aiogram.types import CallbackQuery

from core import (
    message_templates as mt,  # TODO Move hardcoded captions to message templates
)

router = Router(name=__name__)


@router.callback_query(F.data == 'guide_android')
async def guide_android_query_handler(query: CallbackQuery):
    await query.bot.send_video(
        chat_id=query.from_user.id,
        video='BAACAgIAAxkDAAIEJmkfJdH4uv9-9UnuU3U4goxZSRR5AAJiiAACHbABSYLypmjt8MOmNgQ',
        caption='Делайте всё чётко по инструкции в видео и у вас всё получится!',
    )
    await query.answer()


@router.callback_query(F.data == 'guide_apple')
async def guide_apple_query_handler(query: CallbackQuery):
    await query.bot.send_video(
        chat_id=query.from_user.id,
        video='BAACAgIAAxkDAAIEF2kfILBeYgk17_nY-AQU4BmJmL1aAALrhwACHbABSc_TgJfvZ8cDNgQ',
        caption='Делайте всё чётко по инструкции в видео и у вас всё получится!',
    )
    await query.answer()


@router.callback_query(F.data == 'guide_windows')
async def guide_windows_query_handler(query: CallbackQuery):
    await query.bot.send_video(
        chat_id=query.from_user.id,
        video='BAACAgIAAxkDAAIEMWkfMxtAf4UL2qA9GhUK7Iit1F4KAAKGiQACHbABSYEcfVEs8MyDNgQ',
        caption='Ссылка на скачивание: https://github.com/hiddify/hiddify-app\n\nДелайте всё чётко по инструкции в видео и у вас всё получится!',
    )
    await query.answer()
