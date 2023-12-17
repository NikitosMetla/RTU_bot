import traceback
from functools import wraps

from aiogram.fsm.context import FSMContext

from data.keyboards import profile_keyboard, buy_or_sell_keyboard
from aiogram import types, Bot


def is_username(func):
    @wraps(func)
    async def wrapper(message: types.Message | types.CallbackQuery, state: FSMContext | None, bot: Bot | None, **kwargs):
        print("========================= " + func.__name__ + " ============================")
        try:
            if message.from_user.username is not None:
                print('Проверка на наличие username пройдена')
                return await func(message, state, bot, **kwargs)
            elif type(message) == types.Message:
                await message.delete()
                await message.answer("Вы не можете воспользоваться продавать вещи или же редактировать свои объявления,"
                                     " так как у вас отстутствует telegram"
                                     " username, который необходим для контакта с вами."
                                     " Его можно сделать в настройках telegram в разделе <i>Мой аккаунт</i>",
                                     reply_markup=buy_or_sell_keyboard.as_markup())
            else:
                await message.message.edit_text("Вы не можете воспользоваться данным разделом, так как у вас отстутствует telegram"
                                             " username. Его можно сделать в настройках telegram"
                                             " в разделе <i>Мой аккаунт</i>")
                await message.message.edit_reply_markup(reply_markup=buy_or_sell_keyboard.as_markup())
        except Exception:
            print(traceback.format_exc())
        finally:
            print("========================= " + func.__name__ + " ============================")
    return wrapper
