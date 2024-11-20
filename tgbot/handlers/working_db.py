import stat
from tgbot.constants_helpers import constant_keyboard as ck
from tgbot.data import config
from tgbot.filters.callback_data import SaveMenuCallback
from tgbot.database.databaseutils import DatabaseManager
from tgbot.api.notionapi import create_page
from tgbot.api.parsin_url import main as get_data_url
from tgbot.keyboards import replykeyboard as rk, inlinekeyboard as ik
from tgbot.nlp_test.text_priority import analyze_priority
from tgbot.states.states import Form

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
    await state.set_state(Form.user_pick_link)
    user_data = await state.get_data()
    # selected_link = user_data.get("pick_link")
    user_choose_link = user_data.get("user_pick_link")

    if not user_choose_link:
        await query.answer("Нет выбранных ссылок.")
        return

    # data_url =await get_data_url(user_choose_link)
    # print(data_url)

    # priority = analyze_priority(data_url[][2])
    # print(priority)

    for link in user_choose_link:
        """Сохранение в обе базе данных"""
        domain = urlparse(link).netloc or "Unknown"
        user_id = query.from_user.id
        notion_page_id = await create_page(link, user_id, domain)
        # Для сохранение в базе данных
        success_url = db_manager.save_user_links(link, user_id, domain)
    if success_url and notion_page_id:
        await query.answer("Ваши ссылки были сохранены в обеих базах данных!")

    await query.message.answer(
        text="Выберите категорий который классифируете ваши urls ",
        reply_markup=rk.add_cat_kb(),
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


@db_router.message(Form.user_pick_link)
async def process_cat(message: Message, state: FSMContext):
    category_user_pick = message.text
    user_id = message.from_user.id
    # Получаем данные пользователя из состояния
    user_data = await state.get_data()
    user_choose_link = user_data.get("user_pick_link")
    data_url = await get_data_url(user_choose_link)
    success =await db_manager.save_data_url(
        data_url=data_url,
        category=category_user_pick,
        user_id=user_id,
        user_link=user_choose_link,
    )
    await state.clear()
    await message.answer("успешно")
