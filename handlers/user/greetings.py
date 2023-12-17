from aiogram import types, Bot
from aiogram import Router
from aiogram.filters import  Text, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import any_state

from data.keyboards import profile_keyboard
from db.users import Users
from utils.is_auth import is_auth
from data.settings import InputMessage


greeting_router = Router()


@greeting_router.message(CommandStart(), any_state)
@is_auth
async def start(message: types.Message, state: FSMContext, bot: Bot):
    await state.clear()
    print(message.from_user.id)
    await message.delete()
    user_data = Users(user_id=message.from_user.id)
    if await user_data.get_auth():
        return await message.answer('<b>👋Привет, ты успешно авторизирован! Выбери свои дальнейшие действия!</b>',
                                    reply_markup=profile_keyboard)


@greeting_router.message(Text(text='Авторизация', ignore_case=True))
async def auth_user(message: types.Message, state: FSMContext):
    user_data = Users(user_id=message.from_user.id)
    if await user_data.get_auth():
        return message.answer('<b>Вы уже авторизированы в системе</b>', reply_markup=profile_keyboard)
    message2 = await message.answer('<b>Для авторизации, следуйте дальнейшим действиям, что просит от вас бот:\n'
                         'Пришлите email в виде: login@edu.mirea.ru</b>')
    print(message.from_user.id)

    await state.set_state(InputMessage.input_email)