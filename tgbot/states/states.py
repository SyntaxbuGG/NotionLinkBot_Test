from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
  
    get_link = State()

    pick_link = State()
    user_pick_link = State()
    save_menu_kb = State()


class SaveForm(StatesGroup):
    after_save = State()


class SettingForm(StatesGroup):
    get_id_token =  State()
