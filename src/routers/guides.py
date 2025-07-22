from aiogram import F, Router
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder

from core import message_templates as mt

router = Router(name=__name__)


@router.callback_query(F.data == 'guide_android')
async def guide_android_query_handler(query: CallbackQuery):
    media_group_builder = MediaGroupBuilder(caption=mt.guide_android)
    for i in range(1, 8):
        media_group_builder.add_photo(FSInputFile(f'./assets/android/{i}.jpg'))
    await query.bot.send_media_group(
        chat_id=query.from_user.id, media=media_group_builder.build()
    )
    await query.answer()


@router.callback_query(F.data == 'guide_apple')
async def guide_apple_query_handler(query: CallbackQuery):
    media_group_builder = MediaGroupBuilder(caption=mt.guide_apple)
    for i in range(1, 6):
        media_group_builder.add_photo(FSInputFile(f'./assets/ios/{i}.jpg'))
    await query.bot.send_media_group(
        chat_id=query.from_user.id, media=media_group_builder.build()
    )
    await query.answer()


@router.callback_query(F.data == 'guide_windows')
async def guide_windows_query_handler(query: CallbackQuery):
    media_group_builder = MediaGroupBuilder(caption=mt.guide_windows)
    for i in range(1, 8):
        media_group_builder.add_photo(FSInputFile(f'./assets/windows/{i}.jpg'))
    await query.bot.send_media_group(
        chat_id=query.from_user.id, media=media_group_builder.build()
    )
    await query.answer()
