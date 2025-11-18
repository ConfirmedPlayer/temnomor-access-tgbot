import asyncio
from datetime import datetime, timedelta

from aiomoney.schemas import InvoiceSource

from core import message_templates as mt
from core.config import bot, env, scheduler, x_ui_session, yoomoney
from core.types import Minutes, StringifiedUUID, TelegramUserId
from keyboards import user_keyboard
from tools.functions import (
    add_subscription_and_send_message,
    send_message_and_delete_previous,
)


async def create_invoice_url(
    payment_id: StringifiedUUID,
    telegram_user_id: TelegramUserId,
    subscription_name: str,
    amount_rub: int = env.SUBSCRIPTION_PRICE_RUBLES,
    redirect_url: str = env.TELEGRAM_BOT_URL,
) -> str:
    payment_form = await yoomoney.create_invoice(
        amount_rub=amount_rub,
        label=payment_id,
        success_redirect_url=redirect_url,
        payment_source=InvoiceSource.YOOMONEY_WALLET,
    )
    scheduler.add_job(
        func=check_payment_in_background,
        kwargs={
            'payment_id': payment_id,
            'telegram_user_id': telegram_user_id,
            'subscription_name': subscription_name,
        },
        next_run_time=datetime.now(),
    )
    # return 'https://temnomor.ru/'
    return payment_form.url


async def create_renewal_invoice_url(
    payment_id: StringifiedUUID,
    telegram_user_id: TelegramUserId,
    subscription_uuid: StringifiedUUID,
    amount_rub: int = env.SUBSCRIPTION_PRICE_RUBLES,
    redirect_url: str = env.TELEGRAM_BOT_URL,
) -> str:
    payment_form = await yoomoney.create_invoice(
        amount_rub=amount_rub,
        label=payment_id,
        success_redirect_url=redirect_url,
        payment_source=InvoiceSource.YOOMONEY_WALLET,
    )
    # return 'https://temnomor.ru/'
    return payment_form.url


async def is_payment_successful(payment_id: StringifiedUUID) -> bool:
    # return random.choice((True, False, False))
    return await yoomoney.is_payment_successful(payment_id)


async def check_payment_in_background(
    payment_id: StringifiedUUID,
    telegram_user_id: TelegramUserId,
    subscription_name: str,
    how_long: Minutes = 15,
) -> None:
    future = datetime.now() + timedelta(minutes=how_long)
    while datetime.now() < future:
        await asyncio.sleep(60)
        payment_successful = await is_payment_successful(payment_id)
        if payment_successful:
            subscription = await x_ui_session.get_client_settings_by_email(
                email=f'{telegram_user_id}-{subscription_name}'
            )
            if not subscription:
                return await add_subscription_and_send_message(
                    telegram_user_id=telegram_user_id,
                    payment_id=payment_id,
                    subscription_name=subscription_name,
                )
            else:
                return
        else:
            continue

    await bot.send_message(chat_id=telegram_user_id, text=mt.payment_expired)

    return await send_message_and_delete_previous(
        chat_id=telegram_user_id,
        text=mt.command_start,
        redis_key='start_message',
        reply_markup=user_keyboard,
    )
