from tgbot.keyboards import replykeyboard as rk, inlinekeyboard as ik
from tgbot.constants_helpers import constant_keyboard as ck
from tgbot.states.states import Form
from tgbot.filters.callback_data import ChooseCallback, SaveMenuCallback

from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext

from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery


router = Router()


@router.message(CommandStart(ignore_case=True))
async def start_command_handler(message: Message, state: FSMContext ,bot :Bot):
    await state.clear()
    
    from_user = message.from_user.full_name


    greeting_text = f"Добро пожаловать {from_user} 👋 \nЧем могу помочь? 😊"

    await message.answer(greeting_text, reply_markup=rk.first_kb_view())


@router.message(F.text == ck.link_extract)
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

    if message.entities:
        for index, entity in enumerate(message.entities):
            if entity.type == "url":
                link = f"{message.text[entity.offset : entity.offset + entity.length]}"
                url.append(link)
                url_links[index] = link
                builder.button(
                    text=f"{message.text[entity.offset:entity.offset+entity.length]}",
                    callback_data=ChooseCallback(
                        chosen=index, get_link="constanta"
                    ).pack(),
                )

        builder.adjust(2).as_markup()
        await state.update_data(pick_link=url_links)
    if url:
        await message.answer(
            text="Выберите ссылки для сохранение:", reply_markup=builder.as_markup()
        )
    else:
        await message.reply("Ссылка не найдена.")
        await state.set_state(Form.get_link)


@router.callback_query(ChooseCallback.filter(F.get_link == "constanta"), Form.pick_link)
async def chosen_links_handler(
    query: CallbackQuery, callback_data: ChooseCallback, state: FSMContext
):
    user_data = await state.get_data()
    save_menu_added = user_data.get("save_menu_kb", False)
    selected_user = user_data.get("pick_link", {})
    user_send_link = user_data.get("user_pick_link", [])

    chosen_index = callback_data.chosen
    updated_user = {}

    for key, value in selected_user.items():
        # если в начале ссылки смайлик убирает его чтобы когда будет работать несколько раз итерации не добавился смайлики больше
        green_view_link = (
            f"{ck.onfullstop}{value.lstrip(ck.offfullstop)}"
            if not value.startswith(ck.onfullstop)
            else value
        )
        white_view_link = (
            f"{ck.offfullstop}{value.lstrip(ck.onfullstop)}"
            if not value.startswith(ck.offfullstop)
            else value
        )

        if key == chosen_index:
            if value.startswith(f"{ck.onfullstop}"):
                # Если ссылка уже выбрана (с зеленой точкой), делаем её белой
                updated_user[key] = white_view_link
            else:
                # Если ссылка не выбрана, добавляем её с зеленой точкой
                updated_user[key] = green_view_link

        else:
            updated_user[key] = value

    # Содержит ссылки только те которые пользователь добавил
    user_send_link = [
        emoji[1:] for emoji in updated_user.values() if emoji.startswith(ck.onfullstop)
    ]

    await state.update_data(pick_link=updated_user, user_pick_link=user_send_link)

    # Получаем текущую кнопку
    current_keyboard = query.message.reply_markup
    # добавляем кнопки save , back
    save_button = ik.InlineKeyboardButton(
        text=ck.save, callback_data=SaveMenuCallback(save_state=ck.save).pack()
    )
    menu_button = ik.InlineKeyboardButton(
        text=ck.menu, callback_data=SaveMenuCallback(save_state=ck.menu).pack()
    )

    if not save_menu_added:
        current_keyboard.inline_keyboard.append([save_button, menu_button])
        await state.update_data(save_menu_kb=True)

    links_text = "\n".join(f"{link} 🔗" for link in updated_user.values())
    # await query.answer(f"{links_text}")
    await query.message.edit_text(links_text, reply_markup=current_keyboard)
