import aiohttp
from aiogram import Bot, types
from aiogram import Router
from aiogram.fsm.context import FSMContext

from api.lks import LKS
from data.keyboards import profile_keyboard
from data.settings import InputMessage
from db.users import Users
from handlers.user.profile import profile

auth_router = Router(name='auth_router')


@auth_router.message(InputMessage.input_email)
async def input_email(message: types.Message, state: FSMContext):
    if message.text.endswith('@edu.mirea.ru'):
        email = message.text
        await state.set_state(InputMessage.input_password)
        await message.delete()
        message = await message.answer('Пришлите пароль от личного кабинета')
        return await state.update_data(email=email, cancel_message_id=message.message_id)
    await message.reply('Email не проходит валидацию, попробуйте еще раз')


@auth_router.message(InputMessage.input_password)
async def input_password(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await state.clear()
    password = message.text
    await message.delete()
    await bot.delete_message(chat_id=message.from_user.id, message_id=data['cancel_message_id'])
    async with aiohttp.ClientSession() as session:
        lks_api = LKS(session=session, email=data['email'], password=password)
        answer = await lks_api.auth()
        if answer['error']:
            await message.answer(f'Произошла ошибка: {answer["error"]}, попробуйте выполнить авторизацию заново')
        if answer['is_auth']:
            initials = await lks_api.get_profile()
            initials = initials[0].get("ФИО")
            await message.answer('Вы успешно авторизовались в боте!', reply_markup=profile_keyboard)
            user_data = Users(user_id=message.from_user.id)
            cookies_jar = await lks_api.export_cookies()
            await user_data.add_new_user(None, None, data['email'], message.text, None,
                                         None, cookies_jar, initials=initials)
            await profile(message, state, bot)



