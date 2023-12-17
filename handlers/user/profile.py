import aiohttp
from aiogram import Bot, types, F
from aiogram import Router
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import any_state
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from api.lks import LKS
from data.keyboards import cancel_keyboard, inline_add_data_keyboard, profile_keyboard
from data.settings import InputMessage
from db.all_dormitories import Dormitory
from db.users import Users
from utils.is_auth import is_auth


profile_router = Router(name='profile_router')


@profile_router.callback_query(Text(text='get_profile'), any_state)
@profile_router.message(Text(text="Личный кабинет", ignore_case=True))
@is_auth
async def profile(message_data: types.Message | types.CallbackQuery, state: FSMContext, bot: Bot):
    await state.clear()
    inline_profile_keyboard = InlineKeyboardBuilder()
    user_data = Users(user_id=message_data.from_user.id)
    cookies = await user_data.get_cookies()
    email = await user_data.get_email()
    password = await user_data.get_password()
    async with aiohttp.ClientSession(cookies=cookies) as session:
        lks_api = LKS(session=session, email=email, password=password)
        lks_user_data = await lks_api.get_profile()

    profile_info = 'Информация о вашем личном кабинете:\n' \
                   f'Telegram ID: <code>{message_data.from_user.id}</code>\n' \
                   f'Telegram Username: <code>@{message_data.from_user.username}</code>\n' \
                   f'Логин: <code>{email}</code>\n'

    for key in lks_user_data[0].keys():
        profile_info += f'{key}: {lks_user_data[0][key]}\n'

    inline_profile_keyboard.row(
        InlineKeyboardButton(text='Узнать подробную информацию о профиле', callback_data='get_full_profile'))

    if not await user_data.get_code():
        inline_profile_keyboard.row(
            InlineKeyboardButton(text='Добавить секретный пароль', callback_data='add_secret_code'))
    else:
        inline_profile_keyboard.row(
            InlineKeyboardButton(text='Изменить секретный пароль', callback_data='change_secret_code'))

    if not await user_data.get_number_of_obchaga():
        inline_profile_keyboard.row(InlineKeyboardButton(text='Добавить общежитие', callback_data='add_id_obchaga'))
    else:
        profile_info += f'Номер общежития: <code>{await user_data.get_number_of_obchaga()}</code>\n'

    if not await user_data.get_room() and await user_data.get_number_of_obchaga():
        inline_profile_keyboard.row(InlineKeyboardButton(text='Добавить номер комнаты', callback_data='add_id_room'))
    elif await user_data.get_room() and await user_data.get_number_of_obchaga():
        profile_info += f'Номер комнаты: <code>{await user_data.get_room()}</code>\n'

    if not await user_data.get_floor() and await user_data.get_number_of_obchaga():
        inline_profile_keyboard.row(InlineKeyboardButton(text='Добавить номер этажа', callback_data='add_id_floor'))
    elif await user_data.get_floor() and await user_data.get_number_of_obchaga():
        profile_info += f'Номер этажа: <code>{await user_data.get_floor()}</code>\n'

    if await user_data.get_floor() and await user_data.get_room():
        dormitory = Dormitory(obchaga=await user_data.get_number_of_obchaga(), floor=await user_data.get_floor())
        if not await dormitory.student_in_obchaga(message_data.from_user.id, await user_data.get_room()):
            await dormitory.add_student(message_data.from_user.id, await user_data.get_room())

    if type(message_data) == types.Message:
        await message_data.answer(f'<b>{profile_info}</b>', reply_markup=inline_profile_keyboard.as_markup())
    else:
        await message_data.message.edit_text(f'<b>{profile_info}</b>', reply_markup=inline_profile_keyboard.as_markup())


@profile_router.callback_query(Text(text='get_full_profile'), any_state)
@is_auth
async def get_full_profile(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    profile_info = 'Подробная информация о вашем личном кабинете:\n'
    inline_profile_keyboard = InlineKeyboardBuilder()
    user_data = Users(user_id=call.from_user.id)
    cookies = await user_data.get_cookies()
    email = await user_data.get_email()
    password = await user_data.get_password()
    async with aiohttp.ClientSession(cookies=cookies) as session:
        lks_api = LKS(session=session, email=email, password=password)
        lks_user_data = await lks_api.get_profile()

    for key in lks_user_data[1].keys():
        profile_info += f'{key}: <i>{lks_user_data[1][key]}</i>\n'

    for key in lks_user_data[2].keys():
        profile_info += f'{key}: <i>{lks_user_data[2][key]}</i>\n'

    inline_profile_keyboard.row(InlineKeyboardButton(text='Вернуться в личный кабинет', callback_data='get_profile'))

    await call.message.edit_text(text=f'<b>{profile_info}</b>', reply_markup=inline_profile_keyboard.as_markup())


@profile_router.callback_query(Text(startswith='add_'), any_state)
@is_auth
async def add_user_data_in_profile(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    inline_add_data_keyboard = InlineKeyboardBuilder()
    inline_add_data_keyboard.row(InlineKeyboardButton(text='Вернуться в личный кабинет', callback_data='get_profile'))
    user_data = Users(call.from_user.id)
    if not await user_data.get_code() and call.data == 'add_secret_code':
        await state.set_state(InputMessage.input_user_data)
        await state.update_data(user_data='add_secret_code', cancel_message_id=call.message.message_id)
        await call.message.edit_text('<b>Пришлите мне новый секретный ключ, состоящий из цифр (минимум 4 символа)\n'
                                     'ЗАПОМНИТЕ ЕГО!</b>', reply_markup=inline_add_data_keyboard.as_markup())

    elif not await user_data.get_number_of_obchaga() and call.data == 'add_id_obchaga':
        """
        Изменить способ добавления
        """
        inline_add_id_obchaga = InlineKeyboardBuilder()
        inline_add_id_obchaga.row(InlineKeyboardButton(text='Первая', callback_data='obchaga_select_first'))
        inline_add_id_obchaga.row(InlineKeyboardButton(text='Вернуться в личный кабинет', callback_data='get_profile'))
        await call.message.edit_text('<b>Выберете номер общежития</b>',
                                     reply_markup=inline_add_id_obchaga.as_markup())

    elif not await user_data.get_room() and await user_data.get_number_of_obchaga() and call.data == 'add_id_room':
        await state.set_state(InputMessage.input_user_data)
        await state.update_data(user_data='add_id_room', cancel_message_id=call.message.message_id)
        await call.message.edit_text('<b>Пришлите мне номер комнаты</b>',
                                     reply_markup=inline_add_data_keyboard.as_markup())

    elif not await user_data.get_floor() and await user_data.get_number_of_obchaga() and call.data == 'add_id_floor':
        await state.set_state(InputMessage.input_user_data)
        await state.update_data(user_data='add_id_floor', cancel_message_id=call.message.message_id)
        await call.message.edit_text('<b>Пришлите мне номер этажа</b>',
                                     reply_markup=inline_add_data_keyboard.as_markup())


@profile_router.callback_query(Text(startswith='obchaga_select'))
@is_auth
async def select_first_obchaga(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    if call.data == 'obchaga_select_first':
        user_data = Users(call.from_user.id)
        await user_data.add_number_for_obchaga(1)
    await call.message.edit_text('<b>Настройки успешно сохранены</b>')
    await profile(call, state, bot)


@profile_router.message(InputMessage.input_user_data)
@is_auth
async def add_new_user_data(message: types.Message, state: FSMContext, bot: Bot):
    if not message.text.isdigit():
        return await message.reply('Вы неправильно ввели число, попробуйте еще раз..')
    state_user_data: str = (await state.get_data()).get('user_data')
    cancel_message_id: int = (await state.get_data()).get('cancel_message_id')
    await state.clear()
    user_data = Users(message.from_user.id)
    if state_user_data == 'add_id_floor':
        await user_data.add_id_floor(message.text)
    elif state_user_data == 'add_id_room':
        await user_data.add_id_room(message.text)
    elif state_user_data == 'add_secret_code':
        await user_data.add_secret_code(message.text)
    await message.delete()
    await bot.edit_message_text(chat_id=message.from_user.id, message_id=cancel_message_id,
                                text='<b>Настройки успешно сохранены!</b>')
    await profile(message, state, bot)


@profile_router.callback_query(Text(text='change_secret_code'))
@is_auth
async def change_secret_code(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    await call.message.edit_text("Для подтверждения напиши свой email от ЛКС в виде login@edu.mirea.ru",
                                 reply_markup=inline_add_data_keyboard.as_markup())
    await state.set_state(InputMessage.enter_email2)
    await state.update_data(message_id=call.message.message_id)


@profile_router.message(F.text, InputMessage.enter_email2)
@is_auth
async def enter_my_mail(message: types.Message, state: FSMContext, bot: Bot):
    message_id = await state.get_data()
    if message.text == await Users(str(message.from_user.id)).get_email():
        await message.delete()
        await bot.edit_message_text("Отлично, напиши свой пороль от ЛКС",
                                    chat_id=message.from_user.id, message_id=message_id.get('message_id'),
                                    reply_markup=inline_add_data_keyboard.as_markup())
        await state.set_state(InputMessage.enter_password2)
        await state.update_data(message_id)
    else:
        await message.delete()
        await bot.edit_message_text("Ты ввел неверный email, попробуй повторить!",
                                    chat_id=message.from_user.id, message_id=message_id.get("message_id"),
                                    reply_markup=inline_add_data_keyboard.as_markup())


@profile_router.message(F.text, InputMessage.enter_password2)
@is_auth
async def enter_my_password(message: types.Message, state: FSMContext, bot: Bot):
    message_id = await state.get_data()
    if message.text == await Users(str(message.from_user.id)).get_password():
        await message.delete()
        await bot.edit_message_text(text="Отлично, теперь введи свой новый секретный код!",
                                    chat_id=message.from_user.id, message_id=message_id.get('message_id'),
                                    reply_markup=inline_add_data_keyboard.as_markup())
        await state.set_state(InputMessage.enter_code2)
        await state.update_data(message_id=message_id.get("message_id"))
    else:
        try:
            await message.delete()
            await bot.edit_message_text(text="Ты ввел неверный пороль, попробуй повторить!",
                                        chat_id=message.from_user.id, message_id=message_id.get('message_id'),
                                        reply_markup=inline_add_data_keyboard.as_markup())
        except:
            await message.delete()


@profile_router.message(F.text, InputMessage.enter_code2)
@is_auth
async def enter_new_code(message: types.Message, state: FSMContext, bot: Bot):
    if message.text.isdigit():
        await message.delete()
        await Users(str(message.from_user.id)).add_secret_code(int(message.text))
        await message.answer("Твой секретный код изменен!", reply_markup=profile_keyboard)
        message_id = await state.get_data()
        message_id = message_id.get("message_id")
        await bot.delete_message(chat_id=message.from_user.id, message_id=message_id)
        await state.clear()
    else:
        try:
            await message.delete()
            await message.reply("Твой код должен состоять только из цифр, попробуй еще раз!",
                                reply_markup=inline_add_data_keyboard.as_markup())
        except:
            await message.delete()