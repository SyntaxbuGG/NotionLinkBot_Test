# from tgbot.constants_helpers import constant_keyboard
# from tgbot.data import config
# from tgbot.filters.callback_data import ChooseCallback

# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from aiogram.fsm.context import FSMContext
# from aiogram import Router , F
# from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

# db_router = Router()

# engine = create_engine(config.DATABASE_URL, echo=True)

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# @db_router.callback_query(ChooseCallback.filter(F.save_state == constant_keyboard.save))
# async def save_db_notion_handler(
#     query: CallbackQuery, callback_data: ChooseCallback, state: FSMContext
# ):
#     # Получаем данные пользователя из состояния
#     user_data = await state.get_data()
#     selected_link = user_data.get('pick_link')
