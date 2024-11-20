from sys import prefix
from aiogram.filters.callback_data import CallbackData

class ChooseCallback(CallbackData, prefix="my"):
    chosen: int
    get_link: str



class SaveMenuCallback(CallbackData, prefix="save_menu"):
    save_state: str



class ShowLinksCallback(CallbackData,prefix='show'):
    show_links : str