import asyncio
from datetime import datetime

from loguru import logger

from core.config import (
    bot,
    dp,
    http_client,
    redis_storage,
    scheduler,
    x_ui_session,
)
from core.logging import configure_logging
from middlewares import PrivateChatsOnlyMiddleware
from routers import routers
from tools.scheduler_jobs import (
    disallow_simultaneous_connections,
    notify_user_about_subscription_expiration,
)


async def clear_connections() -> None:
    """Closes and clears all connections before shutting down the script"""
    if scheduler.running:
        scheduler.shutdown(wait=False)
    await http_client.close()
    await redis_storage.close()


def add_jobs_to_scheduler() -> None:
    scheduler.add_job(
        func=disallow_simultaneous_connections,
        max_instances=1,
        next_run_time=datetime.now(),
    )

    scheduler.add_job(
        func=notify_user_about_subscription_expiration,
        trigger='interval',
        days=1,
        max_instances=1,
        next_run_time=datetime.now(),
    )


async def main() -> None:
    try:
        await http_client.async_init()

        await x_ui_session.async_init()

        configure_logging()

        dp.include_routers(*routers)

        dp.message.middleware(PrivateChatsOnlyMiddleware())

        scheduler.start()
        # add_jobs_to_scheduler()

        logger.info('Telegram bot polling has started...')
        await dp.start_polling(bot)

    finally:
        await clear_connections()


if __name__ == '__main__':
    asyncio.run(main())
