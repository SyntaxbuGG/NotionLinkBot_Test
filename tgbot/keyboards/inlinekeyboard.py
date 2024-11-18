from aiogram.utils.keyboard import InlineKeyboardBuilder



def add_link_kb():
    builder = InlineKeyboardBuilder()
    
    for index in range(1, 11):
        builder.button(text=f'Выберите {index}',callback_data=f"{index}")

    builder.adjust(4)
    return builder.as_markup()