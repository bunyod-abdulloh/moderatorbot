from aiogram.dispatcher.filters.state import StatesGroup, State


class UserStates(StatesGroup):
    NUMBER_OF_USERS = State()
