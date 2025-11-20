from aiogram import F, Router
from aiogram.types import CallbackQuery, FSInputFile

from core import (
    message_templates as mt,  # TODO Move hardcoded captions to message templates
)

router = Router(name=__name__)


@router.callback_query(F.data == 'guide_android')
async def guide_android_query_handler(query: CallbackQuery):
    await query.bot.send_video(
        chat_id=query.from_user.id,
        video='BAACAgIAAxkDAAIFbWkfNutSRQs6cQmOkU9No1OYYyAhAAIbiwACQggAAUmxT6QKnf8ewDYE',
        caption='Делайте всё чётко по инструкции в видео и у вас всё получится!',
    )
    await query.answer()


@router.callback_query(F.data == 'guide_apple')
async def guide_apple_query_handler(query: CallbackQuery):
    await query.bot.send_video(
        chat_id=query.from_user.id,
        video='BAACAgIAAxkDAAIFb2kfNvemorkeNNQAARM0d2SHHeNBsQACHIsAAkIIAAFJAl2YsH1Dsmo2BA',
        caption='Делайте всё чётко по инструкции в видео и у вас всё получится!',
    )
    await query.answer()


@router.callback_query(F.data == 'guide_windows')
async def guide_windows_query_handler(query: CallbackQuery):
    await query.bot.send_video(
        chat_id=query.from_user.id,
        video='BAACAgIAAxkDAAIFgmkfSJ7gmkgSyhAmExmbNX4NJFZ_AAKAjAACQggAAUkrT0ad2rwm3jYE',
        caption='Ссылка на скачивание: https://github.com/hiddify/hiddify-app\n\nДелайте всё чётко по инструкции в видео и у вас всё получится!\n\n<b>ОБЯЗАТЕЛЬНО запускайте программу от имени Администратора!</b>',
    )
    await query.answer()
