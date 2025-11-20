from aiogram import F, Router
from aiogram.types import CallbackQuery, FSInputFile

from core import (
    message_templates as mt,  # TODO Move hardcoded captions to message templates
)

router = Router(name=__name__)


@router.callback_query(F.data == 'guide_android')
async def guide_android_query_handler(query: CallbackQuery):
    video_file = FSInputFile('./assets/android/android_guide.mp4')
    a = await query.bot.send_video(
        chat_id=query.from_user.id,
        video=video_file,#'BAACAgIAAxkDAAIEJmkfJdH4uv9-9UnuU3U4goxZSRR5AAJiiAACHbABSYLypmjt8MOmNgQ',
        caption='Делайте всё чётко по инструкции в видео и у вас всё получится!',
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
        video=video_file,#'BAACAgIAAxkDAAIEJmkfJdH4uv9-9UnuU3U4goxZSRR5AAJiiAACHbABSYLypmjt8MOmNgQ',
        caption='Делайте всё чётко по инструкции в видео и у вас всё получится!',
    )
    await query.bot.send_message(
        chat_id=query.from_user.id,
        text=a.video.file_id
    )
    await query.answer()


@router.callback_query(F.data == 'guide_windows')
async def guide_windows_query_handler(query: CallbackQuery):
    video_file = FSInputFile('./assets/windows/windows_guide.mp4')
    a = await query.bot.send_video(
        chat_id=query.from_user.id,
        video=video_file,#'BAACAgIAAxkDAAIEJmkfJdH4uv9-9UnuU3U4goxZSRR5AAJiiAACHbABSYLypmjt8MOmNgQ',
        caption='Делайте всё чётко по инструкции в видео и у вас всё получится!',
    )
    await query.bot.send_message(
        chat_id=query.from_user.id,
        text=a.video.file_id
    )
    await query.answer()
