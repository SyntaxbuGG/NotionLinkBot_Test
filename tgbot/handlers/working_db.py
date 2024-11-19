from tgbot.constants_helpers import constant_keyboard
from tgbot.data import config
from tgbot.filters.callback_data import SaveMenuCallback
from tgbot.database.databaseutils import DatabaseManager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from aiogram.fsm.context import FSMContext
from aiogram import Router , F
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

db_router = Router()

engine = create_engine(config.DATABASE_URL, echo=True)


db_manager = DatabaseManager(engine)

@db_router.callback_query(SaveMenuCallback.filter(F.save_state == constant_keyboard.save))
async def save_db_notion_handler(
    query: CallbackQuery, callback_data: SaveMenuCallback, state: FSMContext
):
    # Получаем данные пользователя из состояния
    user_data = await state.get_data()
    selected_link = user_data.get('pick_link')
    
    success = db_manager.save_user_links(selected_link,query)
    
    if success:
        await query.answer("Ваши ссылки были сохранены!")
    else:
        await query.answer("Произошла ошибка при сохранении данных.")

    current_keyboard = query.message.reply_markup
    await query.message.edit_text("Ваши ссылки были сохранены.", reply_markup=current_keyboard)