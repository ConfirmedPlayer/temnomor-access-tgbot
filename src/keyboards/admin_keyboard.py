from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.env import env


def tokenize_callback(__callback_data: str) -> str:
    return __callback_data + env.TELEGRAM_BOT_ADMIN_SECRET


admin_keyboard = InlineKeyboardBuilder()
admin_keyboard.max_width = 1
admin_keyboard.button(
    text='➕ Добавить новую подписку',
    callback_data=tokenize_callback('admin_add_subscription'),
)
admin_keyboard = admin_keyboard.as_markup()
