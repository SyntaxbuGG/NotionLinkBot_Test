from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton , InlineKeyboardMarkup
from tgbot.constants_helpers import constant_keyboard



def add_link_kb():
    builder = InlineKeyboardBuilder()
    
    for index in range(1, 11):
        builder.button(text=f'Выберите {index}',callback_data=f"{index}")
        builder

    builder.adjust(4)
    return builder.as_markup()


def save_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text=constant_keyboard.save , callback_data='save')
    return builder.as_markup()