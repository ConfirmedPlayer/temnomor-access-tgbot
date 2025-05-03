from aiogram.types import CopyTextButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.config import env

user_keyboard = InlineKeyboardBuilder()
user_keyboard.max_width = 2
user_keyboard.button(
    text='🛒 Купить подписку', callback_data='buy_subscription'
)
user_keyboard.button(text='🌐 Мои подписки', callback_data='my_subscriptions')
user_keyboard.button(
    text='Задать вопрос разработчику',
    url=f'https://t.me/{env.TELEGRAM_BOT_ADMIN_USERNAME}',
)
user_keyboard = user_keyboard.as_markup()
