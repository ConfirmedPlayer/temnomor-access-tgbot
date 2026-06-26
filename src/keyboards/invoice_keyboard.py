from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.env import env
from core.types import StringifiedUUID


'''def create_invoice_keyboard(
    payment_id: StringifiedUUID, invoice_url: str
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.max_width = 1
    keyboard.button(
        text=f'💳 Оплатить {env.SUBSCRIPTION_PRICE_RUBLES}₽', url=invoice_url
    )
    keyboard.button(
        text='🧾 Проверить оплату', callback_data=f'payment_id:{payment_id}'
    )
    keyboard.button(
        text='🚫 Отменить покупку', callback_data='cancel_with_warning'
    )
    return keyboard.as_markup()


def create_renewal_invoice_keyboard(
    payment_id: StringifiedUUID, invoice_url: str
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.max_width = 1
    keyboard.button(
        text=f'💳 Оплатить {env.SUBSCRIPTION_PRICE_RUBLES}₽', url=invoice_url
    )
    keyboard.button(
        text='🧾 Проверить оплату',
        callback_data=f'renewal_payment_id:{payment_id}',
    )
    keyboard.button(
        text='🚫 Отменить покупку', callback_data='cancel_with_warning'
    )
    return keyboard.as_markup()
'''