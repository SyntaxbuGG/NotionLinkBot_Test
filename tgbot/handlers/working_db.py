from tgbot.constants_helpers import constant_keyboard as ck
from tgbot.data import config
from tgbot.filters.callback_data import SaveMenuCallback
from tgbot.database.databaseutils import DatabaseManager
from tgbot.api.notionapi import create_page
from tgbot.keyboards import replykeyboard as rk, inlinekeyboard as ik

from sqlalchemy import create_engine
from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message

from urllib.parse import urlparse

db_router = Router()

engine = create_engine(config.DATABASE_URL, echo=True)


db_manager = DatabaseManager(engine)


@db_router.callback_query(SaveMenuCallback.filter(F.save_state == ck.save))
async def save_db_notion_handler(
    query: CallbackQuery, callback_data: SaveMenuCallback, state: FSMContext
):
    # Получаем данные пользователя из состояния
    user_data = await state.get_data()
    selected_link = user_data.get("pick_link")

    if not selected_link:
        await query.answer("Нет выбранных ссылок.")
        return

    for link in selected_link.values():
        if link.startswith(ck.onfullstop):
            link = link[1:]
        else:
            # пропускаем те циклы который пользовтель не выбрал
            continue
        """Сохранение в обе базе данных"""
        domain = urlparse(link).netloc or "Unknown"
        user_id = query.from_user.id
        notion_page_id = await create_page(link, user_id, domain)
        # Для сохранение в базе данных
        success_url = db_manager.save_user_links(link, user_id, domain)
    if success_url and notion_page_id:
        await query.answer("Ваши ссылки были сохранены в обеих базах данных!")
    await state.clear()
    await query.message.answer(
        text=ck.menu_back_kb.format(query.from_user.full_name),
        reply_markup=rk.first_kb_view(),
    )


@db_router.callback_query(SaveMenuCallback.filter(F.save_state == ck.save))
async def back_menu(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await query.message.answer(
        text=ck.menu_back_kb.format(query.from_user.full_name),
        reply_markup=rk.first_kb_view(),
    )


@db_router.message(F.text == ck.my_links)
async def my_links(message: Message):
    get_links_db = db_manager.get_user_links(message.from_user.id)
    print(get_links_db)
    if get_links_db:
        all_links = ik.show_link_kb(get_links_db)
        await message.answer(
            "Выберите ссылку которая хотите добавить данные: ", reply_markup=all_links
        )
    else:
        await message.answer("У вас пока нету сохраненные ссылки")
