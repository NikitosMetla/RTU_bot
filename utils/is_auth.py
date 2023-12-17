import traceback
from functools import wraps

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State

from data.keyboards import start_keyboard
from aiogram import types, Bot
from db.users import Users


def is_auth(func):
    @wraps(func)
    async def wrapper(message: types.Message | types.CallbackQuery, state: FSMContext, bot: Bot, **kwargs):
        print("========================= " + func.__name__ + " ============================")
        try:
            user_data = Users(message.from_user.id)
            if await user_data.get_auth():
                print('Проверка на авторизацию пройдена')
                return await func(message, state, bot, **kwargs)
            elif type(message) == types.Message:
                await message.delete()
                await message.answer('Добрый день, студент!\n'
                         'Для работы в боте нужно выполнить авторизацию, нажмите кнопку "Авторизация" в выпавшей клавиатуре',
                                     reply_markup=start_keyboard)
            else:
                await message.message.answer('Добрый день, студент!\n'
                         'Для работы в боте нужно выполнить авторизацию, нажмите кнопку "Авторизация" в выпавшей клавиатуре',
                                             reply_markup=start_keyboard)
        except Exception:
            print(traceback.format_exc())
        finally:
            print("========================= " + func.__name__ + " ============================")

    return wrapper
