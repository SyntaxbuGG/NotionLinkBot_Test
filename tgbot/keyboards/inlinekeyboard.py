from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from tgbot.constants_helpers import constant_keyboard as ck


def save_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text=ck.save, callback_data="save")
    return builder.as_markup()


def show_link_kb(link):
    builder = InlineKeyboardBuilder()

    for index, value in enumerate(link):
        builder.button(text=f"{value}", callback_data=f"{index}")

    builder.adjust(1)
    return builder.as_markup()


def auto_put_text_kb():
    builder = InlineKeyboardBuilder()

    builder.button(
        text=ck.get_id_token_notion,
        switch_inline_query_current_chat="\nINTEGRATION TOKEN: \nDATABASE: ",

    )

    builder.adjust(1)

    return builder.as_markup()
