from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from tgbot.constants_helpers import constant_keyboard


def first_kb_view():
    builder = ReplyKeyboardBuilder()
    builder.button(text=constant_keyboard.link_extract)
    return builder.adjust(3).as_markup(resize_keyboard=True)



def save_kb():
    builder = ReplyKeyboardBuilder()
    builder.button(text=constant_keyboard.save)
    return builder.as_markup()