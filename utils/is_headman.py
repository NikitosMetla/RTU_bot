import traceback
from functools import wraps

from aiogram.fsm.context import FSMContext

from data.keyboards import profile_keyboard
from aiogram import types, Bot

from db.all_dormitories import Dormitory


def is_main_admin(func):
    @wraps(func)
    async def wrapper(message: types.Message | types.CallbackQuery, state: FSMContext | None, bot: Bot | None, **kwargs):
        print("========================= " + func.__name__ + " ============================")
        try:
            main_admin = Dormitory()
            if await main_admin.is_headman(message.from_user.id):
                print('Проверка на старосту пройдена пройдена')
                return await func(message, state, bot, **kwargs)
            elif type(message) == types.Message:
                await message.delete()
                await message.answer("Вы не являетесь старостой этажа, выберите свои дальнейшие действия!",
                                     reply_markup=profile_keyboard)
            else:
                await message.message.answer("Вы не являетесь старостой этажа, выберите свои дальнейшие действия!",
                                             reply_markup=profile_keyboard)
        except Exception:
            print(traceback.format_exc())
        finally:
            print("========================= " + func.__name__ + " ============================")
    return wrapper
