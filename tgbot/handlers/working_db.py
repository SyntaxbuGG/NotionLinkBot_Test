from tgbot.constants_helpers import constant_keyboard as ck
from tgbot.data import config
from tgbot.filters.callback_data import SaveMenuCallback
from tgbot.database.databaseutils import DatabaseManager
from tgbot.api.notionapi import check_notion_credentials, pages_create_async
from tgbot.api.parsin_url import main as get_data_url
from tgbot.keyboards import replykeyboard as rk, inlinekeyboard as ik
from tgbot.states.states import Form, SettingForm
from tgbot.filters.regexp_filters import pattern_find_id_token

from sqlalchemy.ext.asyncio import create_async_engine
from aiogram.fsm.context import FSMContext
from aiogram import Bot, Router, F
from aiogram.types import (
    CallbackQuery,
    Message,
)


db_router = Router()

engine = create_async_engine(config.DATABASE_URL, echo=True)


db_manager = DatabaseManager(engine)


@db_router.callback_query(SaveMenuCallback.filter(F.save_state == ck.save))
async def save_db_notion_handler(
    query: CallbackQuery, callback_data: SaveMenuCallback, state: FSMContext
):
    # Получаем данные пользователя из состояния
    await state.set_state(Form.user_pick_link)

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
    get_links_db = await db_manager.get_user_links(message.from_user.id)
    if get_links_db:
        all_links = ik.show_link_kb(get_links_db)
        await message.answer(
            "Выберите ссылку которая хотите добавить данные: ", reply_markup=all_links
        )
    else:
        await message.answer("У вас пока нету сохраненные ссылки")


@db_router.message(Form.user_pick_link)
async def process_cat_handler(message: Message, state: FSMContext, bot: Bot):
    category_user_pick = message.text
    user_id = message.from_user.id

    get_source_sender = ""
    chat_type = message.chat.type
    if chat_type:
        get_source_sender = chat_type
    else:
        get_source_sender = "unknown"

    # Получаем данные пользователя из состояния
    user_data = await state.get_data()
    user_choose_link = user_data.get("user_pick_link", [])
    print(get_source_sender)
    data_url = await get_data_url(user_choose_link)
    if not user_choose_link:
        await message.answer("Нет выбранных ссылок.")
        return

    await bot.send_chat_action(message.chat.id, "typing")
    #  для сохранение в notion
    notion_page_id = await pages_create_async(
        links=user_choose_link,
        user_id=user_id,
        source_sender=get_source_sender,
        category=category_user_pick,
        data_urls=data_url,
    )
    # Для сохранение в базе данных
    success_database = await db_manager.save_multiple_links(
        links=user_choose_link,
        user_id=user_id,
        user_get_source=get_source_sender,
        category=category_user_pick,
        data_urls=data_url,
    )

    if success_database:
        await message.answer("Ваши ссылки были сохранены в  базу данных!")
    else:
        await message.answer("Ошибка при сохранение в базу данных")
    if notion_page_id:
        await message.answer("Ваши ссылки были сохранены в  Notion Database!")
    else:
        await message.answer("Ошибка при сохранение в Notion Database")


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
        id_token_notion=id_token_notion
    )
    
    if check_user_exist_ind_db == 1:
        get_id_token = {
            "INTEGRATION_TOKEN": id_token_notion['integration_token'],
            "DATABASE_ID": id_token_notion['database_id'],
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
