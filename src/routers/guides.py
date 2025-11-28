from aiogram import F, Router
from aiogram.types import CallbackQuery

from core import message_templates as mt

router = Router(name=__name__)


ANDROID_VIDEOGUIDE_TELEGRAM_FILE_ID = 'BAACAgIAAxkDAAIGbmkoSVUKRiXnSiS_Z5KdU6vyWbEcAAKhhgACTKZASXTmqBDtZYIBNgQ'
APPLE_VIDEOGUIDE_TELEGRAM_FILE_ID = 'BAACAgIAAxkDAAIGbGkoSOgQtUIfBBuBYJP9x7pqRQ9qAAKbhgACTKZASed4cE54lQAB5zYE'
WINDOWS_VIDEOGUIDE_TELEGRAM_FILE_ID = 'BAACAgIAAxkDAAIFymkid51O4V_dq9yl1gAB1EVjuUlH2wACNY0AApbYEUny-pLBIMJBTTYE'


@router.callback_query(F.data == 'guide_android')
async def guide_android_query_handler(query: CallbackQuery):
    await query.bot.send_video(
        chat_id=query.from_user.id,
        video=ANDROID_VIDEOGUIDE_TELEGRAM_FILE_ID,
        caption=mt.guide_caption_android,
    )
    await query.answer()


@router.callback_query(F.data == 'guide_apple')
async def guide_apple_query_handler(query: CallbackQuery):
    await query.bot.send_video(
        chat_id=query.from_user.id,
        video=APPLE_VIDEOGUIDE_TELEGRAM_FILE_ID,
        caption=mt.guide_caption_apple,
    )
    await query.answer()


@router.callback_query(F.data == 'guide_windows')
async def guide_windows_query_handler(query: CallbackQuery):
    await query.bot.send_video(
        chat_id=query.from_user.id,
        video=WINDOWS_VIDEOGUIDE_TELEGRAM_FILE_ID,
        caption=mt.guide_caption_windows,
    )
    await query.answer()
