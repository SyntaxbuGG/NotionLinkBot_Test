from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from tgbot.constants_helpers import constant_keyboard as ck


def first_kb_view():
    builder = ReplyKeyboardBuilder()
    builder.button(text=ck.link_extract)
    builder.button(text=ck.my_links)
    return builder.adjust(3).as_markup(resize_keyboard=True)



def save_kb():
    builder = ReplyKeyboardBuilder()
    builder.button(text=ck.save)
    return builder.as_markup()