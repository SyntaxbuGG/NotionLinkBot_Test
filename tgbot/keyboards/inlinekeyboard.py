from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton , InlineKeyboardMarkup
from tgbot.constants_helpers import constant_keyboard




def save_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text=constant_keyboard.save , callback_data='save')
    return builder.as_markup()



def show_link_kb(link):
    builder = InlineKeyboardBuilder()
    
    for index,value in enumerate(link):
        builder.button(text=f'{value}',callback_data=f"{index}")
    
    builder.adjust(1)
    return builder.as_markup()
