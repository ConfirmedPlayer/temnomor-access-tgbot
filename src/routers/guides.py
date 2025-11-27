from aiogram import F, Router
from aiogram.types import CallbackQuery, FSInputFile

from core import message_templates as mt

router = Router(name=__name__)


@router.callback_query(F.data == 'guide_android')
async def guide_android_query_handler(query: CallbackQuery):
    video_file = FSInputFile('./assets/android/android_guide.mp4')
    a = await query.bot.send_video(
        chat_id=query.from_user.id,
        video=video_file,
        caption=mt.guide_caption,
    )
    await query.bot.send_message(
        chat_id=query.from_user.id,
        text=a.video.file_id
    )
    await query.answer()


@router.callback_query(F.data == 'guide_apple')
async def guide_apple_query_handler(query: CallbackQuery):
    video_file = FSInputFile('./assets/ios/ios_macos_guide.mp4')
    a = await query.bot.send_video(
        chat_id=query.from_user.id,
        video=video_file,
        caption=mt.guide_caption,
    )
    await query.bot.send_message(
        chat_id=query.from_user.id,
        text=a.video.file_id
    )
    await query.answer()


@router.callback_query(F.data == 'guide_windows')
async def guide_windows_query_handler(query: CallbackQuery):
    await query.bot.send_video(
        chat_id=query.from_user.id,
        video='BAACAgIAAxkDAAIFymkid51O4V_dq9yl1gAB1EVjuUlH2wACNY0AApbYEUny-pLBIMJBTTYE',
        caption=mt.guide_caption_windows,
    )
    await query.answer()
