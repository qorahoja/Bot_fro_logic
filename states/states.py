from aiogram.dispatcher.filters.state import State, StatesGroup


class States(StatesGroup):
    name = State()  # Define states for your conversation
    car_number = State()    