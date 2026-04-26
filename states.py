from aiogram.fsm.state import StatesGroup, State

class Ward(StatesGroup):
    first = State() #item_name
    second = State() #waiting for category
    third = State() #waiting_for_ material
    fourth = State() #waiting for color

class Adding(StatesGroup):
    photo = State()
    process = State()

