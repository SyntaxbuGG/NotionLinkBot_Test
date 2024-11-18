from aiogram.filters.callback_data import CallbackData

class ChooseCallback(CallbackData, prefix="my"):
    chosen: int
    get_link: str
