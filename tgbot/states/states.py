from aiogram.fsm.state import StatesGroup, State

class Form(StatesGroup):
    get_link = State()
    all_links = State()
    pick_link = State()
    save_menu_kb = State()
