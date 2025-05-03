from aiogram.utils.keyboard import InlineKeyboardBuilder

guides_keyboard = InlineKeyboardBuilder()

guides_keyboard.max_width = 1

guides_keyboard.button(
    text='Инструкция для Android 📱', callback_data='guide_android'
)
guides_keyboard.button(
    text='Инструкция для iOS, macOS (iPhone, MacBook и т.д.) 📱💻🍏',
    callback_data='guide_apple',
)
guides_keyboard.button(
    text='Инструкция для Windows 🖥', callback_data='guide_windows'
)

guides_keyboard = guides_keyboard.as_markup()
