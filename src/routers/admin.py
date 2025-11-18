import asyncio

from aiogram import Router
from aiogram.exceptions import TelegramAPIError, TelegramRetryAfter
from aiogram.filters import Filter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from loguru import logger

from core import message_templates as mt
from core.config import bot, env, x_ui_session
from keyboards import admin_keyboard
from states import AdminAddingSubscription, AdminMailing
from tools.functions import (
    new_uuid4_str,
    normalize_subscription_name,
    send_message_and_delete_previous,
    unix_timestamp_in_milliseconds,
    verify_subscription_name,
)

router = Router(name=__name__)


class AdminCommandFilter(Filter):
    def __init__(self, command: str) -> None:
        self.command = command

    async def __call__(self, msg: Message) -> bool:
        if msg.from_user.id == env.TELEGRAM_BOT_ADMIN_ID:
            return msg.text == self.command
        return False


class AdminQueryFilter(Filter):
    def __init__(self, data: str) -> None:
        self.data = data

    async def __call__(self, query: CallbackQuery) -> bool:
        if query.from_user.id == env.TELEGRAM_BOT_ADMIN_ID:
            return query.data.startswith(self.data) and query.data.endswith(
                env.TELEGRAM_BOT_ADMIN_SECRET
            )
        return False


@router.message(AdminCommandFilter('/admin'))
async def admin_command_handler(msg: Message):
    return await send_message_and_delete_previous(
        chat_id=msg.from_user.id,
        text=mt.admin_hello,
        redis_key='admin_message',
        reply_markup=admin_keyboard,
    )


@router.callback_query(AdminQueryFilter('admin_add_subscription'))
async def admin_add_subscription_query_handler(
    query: CallbackQuery, state: FSMContext
):
    await state.set_state(AdminAddingSubscription.reading_telegram_user_id)
    await send_message_and_delete_previous(
        chat_id=query.from_user.id,
        text=mt.admin_prompt_telegram_user_id,
        redis_key='admin_message',
    )
    await query.answer()


@router.message(AdminAddingSubscription.reading_telegram_user_id)
async def admin_reading_telegram_user_id_handler(
    msg: Message, state: FSMContext
):
    telegram_user_id = msg.text
    if not telegram_user_id.isdigit():
        return await msg.answer(mt.admin_incorrect_telegram_user_id)

    await state.set_state(AdminAddingSubscription.reading_expiration_time)
    await state.set_data({'telegram_user_id': telegram_user_id})
    await msg.answer(text=mt.admin_prompt_subscription_expiration)


@router.message(AdminAddingSubscription.reading_expiration_time)
async def admin_reading_expiration_time_handler(
    msg: Message, state: FSMContext
):
    expiration_time = msg.text
    data = await state.get_data()
    data |= {'subscription_expiration': int(expiration_time)}
    await state.set_data(data)
    await state.set_state(AdminAddingSubscription.reading_subscription_name)
    await msg.answer(text=mt.admin_prompt_subscription_name)


@router.message(AdminAddingSubscription.reading_subscription_name)
async def admin_reading_subscription_name_handler(
    msg: Message, state: FSMContext
):
    data = await state.get_data()
    telegram_user_id = data['telegram_user_id']
    subscription_expiration = data['subscription_expiration']
    if subscription_expiration != 0:
        subscription_expiration = unix_timestamp_in_milliseconds(
            add_days=subscription_expiration
        )
    subscription_name = msg.text
    if warning_message := await verify_subscription_name(
        text=subscription_name, telegram_user_id=telegram_user_id
    ):
        return await msg.answer(warning_message)

    subscription_name = normalize_subscription_name(subscription_name)

    await state.clear()

    await x_ui_session.add_new_subscription(
        telegram_user_id=telegram_user_id,
        subscription_uuid=new_uuid4_str(),
        subscription_name=subscription_name,
        subscription_expiration=subscription_expiration,
    )

    await state.clear()

    await msg.answer(text=mt.admin_new_subscription_successful)


@router.message(AdminCommandFilter('/mailing'))
async def mailing_command_handler(msg: Message, state: FSMContext):
    await state.set_state(AdminMailing.reading_message)
    return await send_message_and_delete_previous(
        chat_id=msg.from_user.id,
        text=mt.admin_mailing_hello,
        redis_key='admin_mailing_message',
    )


@router.message(AdminMailing.reading_message)
async def mailing_command_state_handler(msg: Message, state: FSMContext):
    telegram_user_ids = await x_ui_session.get_all_users_telegram_ids()
    for telegram_user_id in telegram_user_ids:
        try:
            await bot.send_message(chat_id=telegram_user_id, text=msg.text)
            logger.info(f'Message sent to {telegram_user_id}')
        except TelegramRetryAfter as _ex:
            await asyncio.sleep(_ex.retry_after + 1)
            await bot.send_message(chat_id=telegram_user_id, text=msg.text)
            logger.info(
                f'Message sent to {telegram_user_id} after TelegramRetryAfter.'
            )
        except TelegramAPIError:
            logger.warning(f'Failed to send message to {telegram_user_id}')
        except Exception:
            await state.clear()

    await state.clear()
    await bot.send_message(
        chat_id=env.TELEGRAM_BOT_ADMIN_ID, text=mt.admin_mailing_success
    )


@router.message(AdminCommandFilter('/test_mailing'))
async def test_mailing_command_handler(msg: Message, state: FSMContext):
    await state.set_state(AdminMailing.reading_test_message)
    return await send_message_and_delete_previous(
        chat_id=msg.from_user.id,
        text=mt.admin_test_mailing_hello,
        redis_key='admin_test_mailing_message',
    )


@router.message(AdminMailing.reading_test_message)
async def test_mailing_command_state_handler(msg: Message, state: FSMContext):
    await bot.send_message(chat_id=env.TELEGRAM_BOT_ADMIN_ID, text=msg.text)
    await state.clear()
