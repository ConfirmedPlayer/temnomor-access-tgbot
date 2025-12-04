from datetime import date, datetime

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, CopyTextButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loguru import logger

import core.message_templates as mt
from core.config import env, x_ui_session
from keyboards import (
    create_renewal_invoice_keyboard,
    guides_keyboard,
    user_keyboard,
)
from states import BuyingSubscription
from tools.functions import (
    new_uuid4_str,
    normalize_subscription_name,
    redis_get_message_id,
    send_message_and_delete_previous,
    update_subscription_and_send_message,
    verify_subscription_name,
)
from tools.payments import create_renewal_invoice_url, is_payment_successful

router = Router(name=__name__)


async def get_user_subscriptions(
    telegram_user_id: int,
) -> list[dict[str, str | date]]:
    user_subscriptions_list = []
    user_subscriptions = (
        await x_ui_session.get_user_subscriptions_by_telegram_id(
            telegram_user_id=telegram_user_id
        )
    )
    for user_subscription in user_subscriptions:
        subscription_email = user_subscription.email
        subscription_name = subscription_email.split('-')[-1]
        subscription_uuid = user_subscription.id
        subscription_expiration = (
            user_subscription.expiryTime / 1000
        )  # from milliseconds
        subscription_expiration_date = datetime.fromtimestamp(
            subscription_expiration
        ).date()
        user_subscriptions_list.append(
            {
                'subscription_uuid': subscription_uuid,
                'subscription_name': subscription_name,
                'subscription_expiration': subscription_expiration_date,
            }
        )
    return user_subscriptions_list


@router.callback_query(F.data == 'my_subscriptions')
async def my_subscriptions_query_handler(query: CallbackQuery):
    user_has_subscriptions = await x_ui_session.user_has_subscriptions(
        query.from_user.id
    )
    if not user_has_subscriptions:
        return await query.answer(
            text=mt.user_has_no_subscriptions, show_alert=True
        )

    user_subscriptions = await get_user_subscriptions(query.from_user.id)
    keyboard = InlineKeyboardBuilder()
    keyboard.max_width = 1
    for subscription in user_subscriptions:
        subscription_uuid = subscription['subscription_uuid']
        name = subscription['subscription_name']
        keyboard.button(
            text=name, callback_data=f'subscription:{subscription_uuid}'
        )
    keyboard.button(text='🔄 Обновить', callback_data='my_subscriptions')
    keyboard.button(
        text='↩️ Главное меню', callback_data='return_to_the_main_menu'
    )

    message_id = await redis_get_message_id(
        f'start_message:{query.from_user.id}'
    )
    try:
        await query.bot.edit_message_text(
            text=mt.my_subscriptions,
            chat_id=query.from_user.id,
            message_id=message_id,
            reply_markup=keyboard.as_markup(),
        )
        await query.answer()
    except TelegramBadRequest:
        await query.answer(text='Новых подписок нет!', show_alert=True)


@router.callback_query(F.data == 'return_to_the_main_menu')
async def return_to_the_main_menu_query_handler(query: CallbackQuery):
    await query.answer()
    return await send_message_and_delete_previous(
        chat_id=query.from_user.id,
        text=mt.command_start,
        redis_key='start_message',
        reply_markup=user_keyboard,
    )


@router.callback_query(F.data.startswith('subscription'))
async def subscription_query_handler(query: CallbackQuery, state: FSMContext):
    subscription_uuid = query.data.replace('subscription:', '', 1)
    subscription = await x_ui_session.get_client_settings_by_uuid(
        client_uuid=subscription_uuid
    )
    subscription_email = subscription.email
    subscription_name = subscription_email.split('-')[-1]
    subscription_url = env.X_UI_SUBSCRIPTION_URL + f'/{subscription.subId}'
    subscription_expiration_date = (
        subscription.expiryTime / 1000
    )  # from milliseconds
    subscription_expiration_date = datetime.fromtimestamp(
        timestamp=subscription_expiration_date
    )
    expired = (
        subscription_expiration_date.year != 1970
        and datetime.now() > subscription_expiration_date
    )
    human_readable_date = subscription_expiration_date.strftime('%d.%m.%Y')

    current_message_id = await redis_get_message_id(
        f'start_message:{query.from_user.id}'
    )
    message = f'Подписка "{subscription_name}" до {human_readable_date} {"(✅ Активна)" if not expired else "(❌ Неактивна)"}'
    keyboard = InlineKeyboardBuilder()
    keyboard.max_width = 1
    keyboard.button(
        text='🛒 Продлить подписку',
        callback_data=f'renew_subscription:{subscription_uuid}',
    )
    if not expired:
        keyboard.button(
            text='📇 Изменить название',
            callback_data=f'rename_subscription:{subscription_uuid}',
        )
        keyboard.button(
            text='🌐 Скопировать',
            copy_text=CopyTextButton(text=subscription_url),
        )
    keyboard.button(text='↩️ Назад', callback_data='my_subscriptions')
    await state.set_data({'subscription_name': subscription_name})
    await query.bot.edit_message_text(
        text=message,
        chat_id=query.from_user.id,
        message_id=current_message_id,
        reply_markup=keyboard.as_markup(),
    )
    if not expired:
        await send_message_and_delete_previous(
            chat_id=query.from_user.id,
            text=mt.copy_subscription_and_check_guide,
            redis_key='guides_message',
            reply_markup=guides_keyboard,
        )
    await query.answer()


@router.callback_query(F.data.startswith('rename_subscription'))
async def rename_subscription_query_handler(
    query: CallbackQuery, state: FSMContext
):
    subscription_uuid = query.data.replace('rename_subscription:', '', 1)

    await state.set_state(BuyingSubscription.rename_subscription)
    await state.set_data({'subscription_uuid': subscription_uuid})

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='↩️ Вернуться в главное меню', callback_data='cancel')

    await send_message_and_delete_previous(
        chat_id=query.from_user.id,
        text=mt.choosing_subscription_name,
        redis_key='start_message',
        reply_markup=keyboard.as_markup(),
    )

    await query.answer()


@router.message(BuyingSubscription.rename_subscription)
async def rename_subscription_state_handler(msg: Message, state: FSMContext):
    subscription_name = msg.text
    if warning_message := await verify_subscription_name(
        text=subscription_name, telegram_user_id=msg.from_user.id
    ):
        return await msg.answer(warning_message)

    subscription_uuid = (await state.get_data())['subscription_uuid']
    await state.clear()
    subscription_name = normalize_subscription_name(subscription_name)

    await x_ui_session.update_client_by_uuid(
        client_uuid=subscription_uuid, subscription_name=subscription_name
    )

    logger.info(
        f'User: {msg.from_user.id} renamed his subscription to {subscription_name}'
    )

    await send_message_and_delete_previous(
        chat_id=msg.from_user.id,
        text=mt.subscription_rename_successful,
        redis_key='start_message',
        reply_markup=user_keyboard,
    )


@router.callback_query(F.data.startswith('renew_subscription'))
async def renew_subscription_query_handler(
    query: CallbackQuery, state: FSMContext
):
    subscription_uuid = query.data.replace('renew_subscription:', '', 1)
    invoice_uuid = new_uuid4_str()
    invoice_url = await create_renewal_invoice_url(
        payment_id=invoice_uuid,
        telegram_user_id=query.from_user.id,
        subscription_uuid=subscription_uuid,
    )
    invoice_keyboard = create_renewal_invoice_keyboard(
        payment_id=invoice_uuid, invoice_url=invoice_url
    )

    await state.set_data({'subscription_uuid': subscription_uuid})

    await send_message_and_delete_previous(
        chat_id=query.from_user.id,
        text=mt.purchase_invoice,
        redis_key='start_message',
        reply_markup=invoice_keyboard,
    )

    await query.answer()


@router.callback_query(F.data.startswith('renewal_payment_id'))
async def check_payment_query_handler(query: CallbackQuery, state: FSMContext):
    payment_id = query.data.replace('renewal_payment_id:', '', 1)
    subscription_uuid = (await state.get_data())['subscription_uuid']
    if await is_payment_successful(payment_id):
        await update_subscription_and_send_message(
            client_uuid=subscription_uuid,
            payment_id=payment_id,
            telegram_user_id=query.from_user.id,
        )
        await state.clear()
        await query.answer()
    else:
        await query.answer(text=mt.payment_unsuccessful, show_alert=True)
