from aiogram.fsm.state import StatesGroup, State

class BotStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_date_birthday = State()
    waiting_for_group = State()
    waiting_for_confirmation_from_user = State()
    waiting_for_confirmation_from_admin = State()
    waiting_for_payment = State()
