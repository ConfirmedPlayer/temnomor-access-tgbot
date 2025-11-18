from aiogram.fsm.state import State, StatesGroup


class BuyingSubscription(StatesGroup):
    reading_rules = State()
    choosing_a_name = State()
    rename_subscription = State()


class AdminAddingSubscription(StatesGroup):
    reading_telegram_user_id = State()
    reading_subscription_name = State()
    reading_expiration_time = State()


class AdminMailing(StatesGroup):
    reading_message = State()
    reading_test_message = State()
