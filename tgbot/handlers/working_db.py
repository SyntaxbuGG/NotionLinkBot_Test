from tgbot.constants_helpers import constant_keyboard as ck
from tgbot.data import config
from tgbot.filters.callback_data import SaveMenuCallback
from tgbot.database.databaseutils import DatabaseManager
from tgbot.api.notionapi import create_page, check_notion_credentials
from tgbot.api.parsin_url import main as get_data_url
from tgbot.keyboards import replykeyboard as rk, inlinekeyboard as ik
from tgbot.states.states import Form, SettingForm
from tgbot.filters.regexp_filters import pattern_find_id_token

from sqlalchemy import create_engine
from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    Message,
    ReplyKeyboardRemove,
)

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
    user_choose_link = user_data.get("user_pick_link")
    user_get_source: str = user_data.get("get_link", {})

    if not user_choose_link:
        await query.answer("Нет выбранных ссылок.")
        return

    user_id = query.from_user.id
    for link in user_choose_link:
        """Сохранение в обе базе данных"""
        source_link = urlparse(link).netloc or "Unknown"
        #  для сохранение в notion
        notion_page_id = await create_page(
            link, user_id, source_link=source_link, source_sender=user_get_source
        )

        # Для сохранение в базе данных
        success_url = db_manager.save_user_links(
            link, user_id, source_link=source_link, source_sender=user_get_source
        )
    if success_url:
        await query.answer("Ваши ссылки были сохранены в  базу данных!")
    else:
        await query.answer("Ошибка при сохранение в базу данных")
    if notion_page_id:
        await query.answer("Ваши ссылки были сохранены в  Notion Database!")
    else:
        await query.answer("Ошибка при сохранение в Notion Database")
    await query.message.answer(
        text="Выберите категорий который классифируете ваши urls ",
        reply_markup=rk.add_cat_kb(),
    )


@db_router.callback_query(SaveMenuCallback.filter(F.save_state == ck.menu))
async def back_menu_handler(query: CallbackQuery, state: FSMContext):
    # очищаем состояник так как вернемся на начале
    await state.clear()

    await query.message.answer(
        text=ck.menu_back_kb.format(query.from_user.full_name),
        reply_markup=rk.first_kb_view(),
    )


@db_router.message(F.text == ck.my_links)
async def my_links_handler(message: Message):
    get_links_db = db_manager.get_user_links(message.from_user.id)
    if get_links_db:
        all_links = ik.show_link_kb(get_links_db)
        await message.answer(
            "Выберите ссылку которая хотите добавить данные: ", reply_markup=all_links
        )
    else:
        await message.answer("У вас пока нету сохраненные ссылки")


@db_router.message(Form.user_pick_link)
async def process_cat_handler(message: Message, state: FSMContext):
    category_user_pick = message.text
    user_id = message.from_user.id
    print(category_user_pick)
    # Получаем данные пользователя из состояния
    user_data = await state.get_data()
    user_choose_link = user_data.get("user_pick_link",[])
    data_url = await get_data_url(user_choose_link)

    succes_save_db = await db_manager.save_data_url(
        data_url=data_url,
        category=category_user_pick,
        user_id=user_id,
        user_link=user_choose_link,
    )
    if succes_save_db:
        await message.answer("Успешно сохранено", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer(ck.error)


@db_router.message(F.text == ck.settings)
async def setting_handler(message: Message):
    await message.answer("Выберите: ", reply_markup=rk.setting_kb())


@db_router.message(F.text == ck.get_id_token_notion)
async def ask_id_token_handler(message: Message, state: FSMContext):
    await state.set_state(SettingForm.get_id_token)
    await message.answer(
        text=ck.notion_db_integration, reply_markup=ik.auto_put_text_kb()
    )


@db_router.message(SettingForm.get_id_token)
async def get_id_token_handler(message: Message):
    user_id = message.from_user.id
    id_token_notion = await pattern_find_id_token(message.text)

    check_user_exist_ind_db = await check_notion_credentials(
        user_id=user_id, id_token_notion=id_token_notion
    )
   
    if check_user_exist_ind_db == 1:
        get_id_token = {
            "INTEGRATION_TOKEN": id_token_notion[0][0],
            "DATABASE_ID": id_token_notion[0][1],
        }

        save_id_token_frombase = await db_manager.save_notion_id_token(
            user_id=user_id,
            integration_token=get_id_token["INTEGRATION_TOKEN"],
            database_id=get_id_token["DATABASE_ID"],
        )
        if save_id_token_frombase:
            await message.answer("Успешно изменено!!!")
        else:
            await message.answer("Один пользовтель один раз может изменить токен")
    elif check_user_exist_ind_db == -1:
        await message.answer("Invalid integration token.")
    elif check_user_exist_ind_db == -2:
        await message.answer("Database ID not found.")
    else:
        await message.answer("Unexpected error")
