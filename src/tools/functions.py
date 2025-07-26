import re
from contextlib import suppress
from datetime import datetime, timedelta
from re import Pattern
from typing import Literal
from uuid import uuid4

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup

from core import message_templates as mt
from core.config import bot, env, redis_storage, x_ui_session
from core.types import (
    MessageTemplate,
    StringifiedUUID,
    TelegramUserId,
    UnixTimeStampInMilliseconds,
)
from keyboards import user_keyboard


def normalize_subscription_name(
    name: str, regex: Pattern[str] = re.compile(r'\s+')
) -> str:
    subscription_name = name.replace('-', ' ')
    subscription_name = regex.sub('_', subscription_name)
    return subscription_name


def unix_timestamp_in_milliseconds(
    add_days: int = 0,
) -> UnixTimeStampInMilliseconds:
    next_date = datetime.now() + timedelta(days=add_days)
    timestamp_in_milliseconds = next_date.timestamp() * 1000  # to milliseconds
    return int(timestamp_in_milliseconds)


def new_uuid4_str() -> StringifiedUUID:
    return str(uuid4())


async def verify_subscription_name(
    text: str, telegram_user_id: TelegramUserId
) -> MessageTemplate | Literal[False]:
    if not text:
        return mt.wrong_subscription_name
    if len(text) > 30:
        return mt.subscription_name_too_long

    user_subscriptions = (
        await x_ui_session.get_user_subscriptions_by_telegram_id(
            telegram_user_id=telegram_user_id
        )
    )
    if any(sub.email.split('-')[-1] == text for sub in user_subscriptions):
        return mt.subscription_name_already_exists

    return False


async def redis_get_message_id(key: str) -> str:
    message_id = await redis_storage.redis.get(key)
    return message_id


async def send_message_and_delete_previous(
    chat_id: int | str,
    text: str,
    redis_key: str,
    reply_markup: InlineKeyboardMarkup | None = None,
    disable_notification: bool = False,
) -> None:
    message = await bot.send_message(
        chat_id=chat_id,
        text=text,
        disable_notification=disable_notification,
        reply_markup=reply_markup,
    )
    if message_id := await redis_get_message_id(f'{redis_key}:{chat_id}'):
        with suppress(TelegramBadRequest):
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
    await redis_storage.redis.set(f'{redis_key}:{chat_id}', message.message_id)


async def add_subscription_and_send_message(
    telegram_user_id: TelegramUserId,
    payment_id: StringifiedUUID,
    subscription_name: str,
) -> None:
    await x_ui_session.add_new_subscription(
        telegram_user_id=telegram_user_id,
        subscription_uuid=payment_id,
        subscription_name=subscription_name,
        subscription_expiration=unix_timestamp_in_milliseconds(add_days=30),
    )
    await send_message_and_delete_previous(
        chat_id=telegram_user_id,
        text=mt.payment_successful,
        redis_key='start_message',
        reply_markup=user_keyboard,
    )


async def update_subscription_and_send_message(
    client_uuid: StringifiedUUID,
    payment_id: StringifiedUUID,
    telegram_user_id: TelegramUserId,
) -> None:
    current_settings = await x_ui_session.get_client_settings_by_uuid(
        client_uuid=client_uuid
    )
    new_expiry_time = (
        int(current_settings.expiryTime) / 1000
    )  # from milliseconds
    new_expiry_time = datetime.fromtimestamp(new_expiry_time) + timedelta(
        days=30
    )
    new_expiry_time = new_expiry_time.timestamp() * 1000  # to milliseconds
    await x_ui_session.update_client_by_uuid(
        client_uuid=client_uuid,
        subscription_expiration=new_expiry_time,
        subscription_comment=payment_id,
    )
    await send_message_and_delete_previous(
        chat_id=telegram_user_id,
        text=mt.payment_successful,
        redis_key='start_message',
        reply_markup=user_keyboard,
    )


def tokenize_callback(__callback_data: str) -> str:
    return __callback_data + env.TELEGRAM_BOT_ADMIN_SECRET
