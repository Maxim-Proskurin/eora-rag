"""
FSM/состояния пользователя для Telegram-бота.
"""

from aiogram.fsm.state import State, StatesGroup


class UserState(StatesGroup):
    choosing_provider = State()
    waiting_for_question = State()