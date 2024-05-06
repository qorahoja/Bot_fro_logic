from aiogram.dispatcher.filters.state import State, StatesGroup


class States(StatesGroup):
    name = State()  # Define states for your conversation
    car_number = State()    
    paid_status = State()
    factoring = State()
    amz_payment = State()
    note = State()
    wait = State()
    wait_amz = State()
    no_note = State()