from ast import For
from re import S
import select
import stat
from turtle import update

import asyncio


from tgbot.keyboards import replykeyboard as rk, inlinekeyboard as ik
from tgbot.constants_helpers import constant_keyboard
from tgbot.states.states import Form
from tgbot.filters.callback_data import ChooseCallback

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery


router = Router()

global_user_pick = set()


@router.message(CommandStart(ignore_case=True))
async def start_command_handler(message: Message, state: FSMContext):
    from_user = message.from_user

    greeting_text = f"С возвращением, {from_user.full_name}! Чем могу помочь?"

    await message.answer(greeting_text, reply_markup=rk.first_kb_view())


@router.message(F.text == constant_keyboard.link_extract)
async def send_text_handler(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Form.get_link)
    await message.answer(
        "Отправьте текст с ссылками", reply_markup=ReplyKeyboardRemove()
    )


@router.message(Form.get_link)
async def get_link_handler(message: Message, state: FSMContext):
    url = []
    url_links = {}
    await state.set_state(Form.pick_link)
    builder = ik.InlineKeyboardBuilder()
    for index, entity in enumerate(message.entities):
        if entity.type == "url":
            link = f"{message.text[entity.offset : entity.offset + entity.length]}"
            url.append(link)
            url_links[index] = link
            builder.button(
                text=f"{message.text[entity.offset:entity.offset+entity.length]}",
                callback_data=ChooseCallback(chosen=index, get_link="constanta").pack(),
            )

    builder.adjust(2).as_markup()
    await state.update_data(pick_link=url_links)
    if url:
        await message.answer(
            text="Выберите ссылки для сохранение:", reply_markup=builder.as_markup()
        )
    else:
        await message.reply("Ссылка не найдена.")


@router.callback_query(ChooseCallback.filter(F.get_link == "constanta"), Form.pick_link)
async def chosen_links_handler(
    query: CallbackQuery, callback_data: ChooseCallback, state: FSMContext
):
    await state.set_state(Form.save_menu_kb)
    user_data = await state.get_data()
    save_menu_added = user_data.get("save_menu_kb", False)
    selected_user = user_data.get("pick_link", {})
    

    chosen_index = callback_data.chosen
    updated_user = {}

    for key, value in selected_user.items():
        green_view_link = f"{constant_keyboard.onfullstop}{value[1:]}"
        white_view_link = f"{constant_keyboard.offfullstop}{value[1:]}"

        if key == chosen_index:
            if value.startswith(f"{constant_keyboard.onfullstop}"):
                # Если ссылка уже выбрана (с зеленой точкой), делаем её белой
                updated_user[key] = white_view_link
            else:
                # Если ссылка не выбрана, добавляем её с зеленой точкой
                updated_user[key] = green_view_link
        else:
            updated_user[key] = value

    # Получаем текущую кнопку
    current_keyboard = query.message.reply_markup
    # добавляем кнопки save , back
    save_button = ik.InlineKeyboardButton(
        text=constant_keyboard.save, callback_data=ChooseCallback(save_state=constant_keyboard.save)
    )
    menu_button = ik.InlineKeyboardButton(
        text=constant_keyboard.menu, callback_data=ChooseCallback(save_state=constant_keyboard.menu)
    )

    
    if not save_menu_added:
        current_keyboard.inline_keyboard.append([save_button, menu_button])
        await state.update_data(save_menu_kb=True)

    await state.update_data(pick_link=updated_user, all_links=updated_user)
    links_text = "\n".join(f"{link} 🔗" for link in updated_user.values())
    # await query.answer(f"{links_text}",)
    await query.message.edit_text(links_text, reply_markup=current_keyboard)


@router.callback_query(ChooseCallback.filter(F.save_state==constant_keyboard.save))
async def save_db_notion_handler(query: CallbackQuery, callback_data: ChooseCallback, state: FSMContext):
    
    