from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

import core.message_templates as mt
from core.config import env, redis_storage, x_ui_session
from core.types import StringifiedUUID, TelegramUserId
from keyboards import create_invoice_keyboard, user_keyboard
from states import BuyingSubscription
from tools.functions import (
    add_subscription_and_send_message,
    new_uuid4_str,
    normalize_subscription_name,
    redis_get_message_id,
    send_message_and_delete_previous,
    unix_timestamp_in_milliseconds,
    verify_subscription_name,
)
from tools.payments import create_invoice_url, is_payment_successful

router = Router(name=__name__)


@router.callback_query(F.data == 'buy_subscription')
async def buy_subscription_query_handler(query: CallbackQuery):
    message_id = await redis_get_message_id(
        f'start_message:{query.from_user.id}'
    )

    user_has_subscriptions = await x_ui_session.user_has_subscriptions(
        query.from_user.id
    )
    if user_has_subscriptions:
        keyboard = InlineKeyboardBuilder()
        keyboard.button(text='↩️ Главное меню', callback_data='cancel')
        keyboard.button(
            text='✅ Я уверен!', callback_data='force_buy_subscription'
        )
        await query.bot.edit_message_text(
            text=mt.user_already_has_subscriptions_warning,
            chat_id=query.from_user.id,
            message_id=message_id,
            reply_markup=keyboard.as_markup(),
        )
        return await query.answer()
    else:
        return await force_buy_subscription_query_handler(query)


@router.callback_query(F.data == 'force_buy_subscription')
async def force_buy_subscription_query_handler(
    query: CallbackQuery, state: FSMContext
):
    message_id = await redis_get_message_id(
        f'start_message:{query.from_user.id}'
    )

    await state.set_state(BuyingSubscription.reading_rules)

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='🚫 Отменить', callback_data='cancel')
    keyboard.button(
        text='✅ Продолжить', callback_data='continue_to_choosing_name'
    )

    await query.bot.edit_message_text(
        text=mt.rules,
        chat_id=query.from_user.id,
        message_id=message_id,
        reply_markup=keyboard.as_markup(),
    )

    await query.answer()


@router.callback_query(F.data == 'cancel')
async def cancel_and_return_to_main_menu(
    query: CallbackQuery, state: FSMContext
):
    await state.clear()
    await send_message_and_delete_previous(
        chat_id=query.from_user.id,
        text=mt.command_start,
        redis_key='start_message',
        reply_markup=user_keyboard,
    )
    await query.answer(text=mt.operation_cancelled, show_alert=True)


@router.callback_query(F.data == 'cancel_with_warning')
async def cancel_with_warning_query_handler(query: CallbackQuery):
    await query.answer(text=mt.operation_cancelled, show_alert=True)
    message_id = await redis_get_message_id(
        f'start_message:{query.from_user.id}'
    )
    await query.bot.edit_message_text(
        text=mt.purchase_cancellation_with_warning,
        chat_id=query.from_user.id,
        message_id=message_id,
        reply_markup=user_keyboard,
    )


@router.callback_query(F.data == 'continue_to_choosing_name')
async def continue_to_choosing_name_query_handler(
    query: CallbackQuery, state: FSMContext
):
    message_id = await redis_get_message_id(
        f'start_message:{query.from_user.id}'
    )
    await query.answer()
    await state.set_state(BuyingSubscription.choosing_a_name)
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='🚫 Отменить', callback_data='cancel')
    await query.bot.edit_message_text(
        text=mt.choosing_subscription_name,
        chat_id=query.from_user.id,
        message_id=message_id,
        reply_markup=keyboard.as_markup(),
    )


@router.message(BuyingSubscription.choosing_a_name)
async def handle_name_and_create_payment(msg: Message, state: FSMContext):
    subscription_name = msg.text
    if warning_message := await verify_subscription_name(
        text=subscription_name, telegram_user_id=msg.from_user.id
    ):
        return await msg.answer(warning_message)

    subscription_name = normalize_subscription_name(subscription_name)

    await state.clear()

    subscription_uuid = new_uuid4_str()
    invoice_url = await create_invoice_url(
        payment_id=subscription_uuid,
        telegram_user_id=msg.from_user.id,
        subscription_name=subscription_name,
    )

    await state.set_data({'subscription_name': subscription_name})

    await send_message_and_delete_previous(
        chat_id=msg.from_user.id,
        text=mt.purchase_invoice,
        redis_key='start_message',
        reply_markup=create_invoice_keyboard(
            payment_id=subscription_uuid, invoice_url=invoice_url
        ),
    )


@router.callback_query(F.data.startswith('payment_id'))
async def check_payment_query_handler(query: CallbackQuery, state: FSMContext):
    payment_id = query.data.replace('payment_id:', '', 1)
    subscription_name = (await state.get_data())['subscription_name']
    if await is_payment_successful(payment_id):
        await add_subscription_and_send_message(
            telegram_user_id=query.from_user.id,
            payment_id=payment_id,
            subscription_name=subscription_name,
        )
        await state.clear()
        await query.answer()
    else:
        await query.answer(text=mt.payment_unsuccessful, show_alert=True)
