from datetime import datetime

import core.message_templates as mt
from core.config import x_ui_session
from keyboards import user_keyboard
from tools.functions import send_message_and_delete_previous
from loguru import logger


async def notify_user_about_subscription_expiration() -> None:
    telegram_users_ids = await x_ui_session.get_all_users_telegram_ids()
    for telegram_user_id in telegram_users_ids:
        all_user_subscriptions = (
            await x_ui_session.get_user_subscriptions_by_telegram_id(
                telegram_user_id=telegram_user_id
            )
        )
        message = ''
        for subscription in all_user_subscriptions:
            subscription_name = subscription.email.split('-')[-1]
            subscription_expire_timestamp = (
                subscription.expiryTime / 1000
            )  # from milliseconds
            subscription_expire_datetime = datetime.fromtimestamp(
                subscription_expire_timestamp
            )

            days_left = (subscription_expire_datetime - datetime.now()).days

            match days_left:
                case 1:
                    message += (
                        mt.subscription_expires_tomorrow.format(
                            subscription_name
                        )
                        + '\n\n'
                    )
                case 3:
                    message += (
                        mt.subscription_expires_in_three_days.format(
                            subscription_name
                        )
                        + '\n\n'
                    )
                case _:
                    continue
        if message:
            await send_message_and_delete_previous(
                chat_id=telegram_user_id,
                text=message,
                redis_key='start_message',
                reply_markup=user_keyboard,
                disable_notification=True,
            )
            logger.info(message)
