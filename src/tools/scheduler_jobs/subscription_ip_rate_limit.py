import asyncio
from datetime import datetime, timedelta
from typing import NoReturn

from loguru import logger

from core import message_templates as mt
from core.config import bot, scheduler, x_ui_session
from core.types import Minutes, Seconds


async def disallow_simultaneous_connections(
    iteration_sleep_time: Seconds = 3,
    turn_back_on_subscription_after: Minutes = 3,
) -> NoReturn:
    try:
        while True:
            online_clients = await x_ui_session.get_all_online_clients()
            for online_client in online_clients:
                ip_addresses = await x_ui_session.get_client_ip_addresses(
                    online_client
                )
                logger.info(ip_addresses)
                if len(ip_addresses) > 1:
                    logger.info(
                        f'The client "{online_client}" was seen abusing (sharing) the '
                        f'subscription with others: {ip_addresses}'
                    )
                    client_settings = (
                        await x_ui_session.get_client_settings_by_email(
                            email=online_client
                        )
                    )
                    await x_ui_session.toggle_subscription_by_uuid(
                        client_uuid=client_settings.id, enable=False
                    )

                    telegram_user_id = online_client.split('-')[0]
                    subscription_name = online_client.split('-')[-1]
                    await bot.send_message(
                        chat_id=telegram_user_id,
                        text=mt.subscription_was_disabled_abusing.format(
                            subscription_name
                        ),
                    )

                    logger.info('adding abusing job...')

                    scheduler.add_job(
                        func=x_ui_session.clear_client_ip_addresses,
                        kwargs={'email': online_client},
                        next_run_time=datetime.now()
                        + timedelta(
                            minutes=turn_back_on_subscription_after - 1
                        ),
                    )

                    scheduler.add_job(
                        func=x_ui_session.toggle_subscription_by_uuid,
                        kwargs={
                            'client_uuid': client_settings.id,
                            'enable': True,
                        },
                        next_run_time=datetime.now()
                        + timedelta(minutes=turn_back_on_subscription_after),
                    )

            await asyncio.sleep(iteration_sleep_time)
    except Exception as _ex:
        logger.exception(f'Exception in IP Rate Limiter: {_ex}')
