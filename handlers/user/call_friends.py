import asyncio
import time

from aiogram import Bot, types, F, Router
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import any_state
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.keyboards import profile_keyboard, start_keyboard, cancel_keyboard, restore_keyboard
from db.all_dormitories import Dormitory
from db.guests_applications import Guests

from db.users import Users

from data.settings import InputMessage
import datetime


call_friends_router = Router()
end_router = Router()


@call_friends_router.message(Text(text="Позвать друга🔶", ignore_case=True))
async def visit_friend(message: types.Message, state: FSMContext, bot: Bot):
    message_for_edit = await message.answer("Отлично, отправь мне ФИО своего гостя, если их несколько, укажи через"
                                            " запятую", reply_markup=cancel_keyboard.as_markup())
    message_id = message_for_edit.message_id
    await state.set_state(InputMessage.calling_guests)
    await state.update_data(message_id=message_id)


@call_friends_router.message(F.text, InputMessage.calling_guests)
async def name_guests(message: types.Message, state: FSMContext, bot: Bot):
    message_id = await state.get_data()
    message_id = message_id.get("message_id")
    await state.set_state(InputMessage.time_guests)
    await state.update_data(initiels=message.text, message_id=message_id)
    guest_initials = message.text
    await bot.edit_message_text(chat_id=message.from_user.id, message_id=message_id,
                                text=f"Отлично, отправь мне приблизительное время к которому {guest_initials}"
                                     f" подойдёт(ут)"
                                     f" (с 9 до 20 часов) "
                                     f"в формате ЧЧ:MM, например, <b>15:20</b>", reply_markup=cancel_keyboard.as_markup())
    await message.delete()


@call_friends_router.message(F.text, InputMessage.time_guests)
async def time_visiting(message: types.Message, state: FSMContext, bot: Bot):
    try:
        data = await state.get_data()
        message_id = data.get("message_id")
        time_visit = datetime.time(int(message.text[:2]), int(message.text[3:]))
        # print(str(time_visit), type(time_visit))
        if datetime.time(9, 0) < time_visit < datetime.time(20, 0):
            data["time"] = time_visit
            # await state.update_data(data)
            await message.delete()
            await bot.edit_message_text(chat_id=message.from_user.id, message_id=message_id,
                                        text="Отлично, отправь мне свой личный код!",
                                        reply_markup=restore_keyboard.as_markup())
            await state.set_state(InputMessage.code_confirm)
            await state.update_data(data)
        else:
            await bot.edit_message_text(chat_id=message.from_user.id, message_id=message_id,
                                        text="В это время нельзя приводить гостей, попробуй уще раз!",
                                        reply_markup=restore_keyboard.as_markup())
    except:
        await message.delete()
        await message.edit_text("Ты ввел неправильный формат времени, попробуй еще раз!",
                                reply_markup=cancel_keyboard)


@call_friends_router.callback_query(Text(text="forget_code", ignore_case=True), InputMessage.code_confirm)
async def forget_code(message: types.CallbackQuery, state: FSMContext, bot: Bot):
    user_code = await Users(str(message.from_user.id)).get_code()
    data = await state.get_data()
    message_id = data.get("message_id")
    if user_code:
        await message.message.edit_text("Для подтверждения напиши свой email от ЛКС в виде login@edu.mirea.ru",
                                        reply_markup=cancel_keyboard.as_markup())
        data = await state.get_data()
        await state.set_state(InputMessage.enter_email)
        await state.update_data(data)
    else:
        await state.clear()
        await bot.delete_message(message_id=message_id, chat_id=message.from_user.id)
        await message.message.answer("Вы не создали код для подтверждений своих действий!"
                                     " Добавьте его вличном кабинете,"
                                     " чтобы пользоваться разделом!", reply_markup=profile_keyboard)


@call_friends_router.message(F.text, InputMessage.enter_email)
async def enter_email(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    message_id = data.get("message_id")
    if message.text == await Users(str(message.from_user.id)).get_email():
        await message.delete()
        await bot.edit_message_text(text="Отлично, напиши свой пороль от ЛКС",
                                    message_id=message_id,
                                    chat_id=message.from_user.id,
                                    reply_markup=cancel_keyboard.as_markup())
        await state.set_state(InputMessage.enter_password)
        await state.update_data(data)
    else:
        await message.delete()
        await bot.edit_message_text(text="Ты ввел неверный email, попробуй повторить!",
                                    message_id=message_id,
                                    chat_id=message.from_user.id,
                                    reply_markup=cancel_keyboard.as_markup())


@call_friends_router.message(F.text, InputMessage.enter_password)
async def enter_password(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    message_id = data.get("message_id")
    user_code = await Users(str(message.from_user.id)).get_password()
    if message.text == user_code and user_code is not None:
        await message.delete()
        await bot.edit_message_text(text="Отлично, напиши свой новый пин-код любой длины (не менее 4 цифр)!",
                                    message_id=message_id,
                                    chat_id=message.from_user.id,
                                    reply_markup=cancel_keyboard.as_markup())
        await state.set_state(InputMessage.enter_code)
        await state.update_data(data)
    elif user_code is None:
        await bot.delete_message(chat_id=message.from_user.id, message_id=message_id)
        await message.answer("Вы не создали код для подтверждений своих действий!"
                                  " Добавьте его вличном кабинете,"
                                  " чтобы пользоваться разделом!", reply_markup=profile_keyboard)
    else:
        await message.delete()
        await bot.edit_message_text(text="Ты ввел неверный пороль, попробуй повторить!",
                                    message_id=message_id,
                                    chat_id=message.from_user.id,
                                    reply_markup=cancel_keyboard.as_markup())


@call_friends_router.message(F.text, InputMessage.enter_code)
async def enter_code(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    message_id = data.get("message_id")
    if message.text.isdigit():
        await message.delete()
        await Users(str(message.from_user.id)).add_secret_code(int(message.text))
        await bot.edit_message_text(text="Отлично твой код обновлен! Введи его для сохранения заявки",
                                    message_id=message_id,
                                    chat_id=message.from_user.id,
                                    reply_markup=cancel_keyboard.as_markup())
        data = await state.get_data()
        await state.set_state(InputMessage.code_confirm)
        await state.update_data(data)
        await message.delete()
    else:
        await bot.edit_message_text(text="Твой код должен состоять только из цифр, попробуй еще раз!",
                                    message_id=message_id,
                                    chat_id=message.from_user.id,
                                    reply_markup=cancel_keyboard.as_markup())


@call_friends_router.message(F.text, InputMessage.code_confirm)
async def confirm_new_code(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    message_id = data.get("message_id")
    user_code = await Users(str(message.from_user.id)).get_code()
    try:
        if message.text == str(await Users(str(message.from_user.id)).get_code()) and user_code:
            await message.delete()
            data = await state.get_data()
            users_api = Users(str(message.from_user.id))
            obchaga = await Users(message.from_user.id).get_number_of_obchaga()
            current_data = datetime.datetime.now()
            application = Guests(user_id=message.from_user.id)
            await application.add_application(friend_initials=data.get('initiels'),
                                              date=str(current_data.day) + "/"
                                                   + str(current_data.month) +
                                                   "/" + str(current_data.year),
                                              time=str(data.get('time'))
                                              )
            application_id = application.application_id
            confirm_friend_keyboard = InlineKeyboardBuilder()
            confirm_friend_keyboard.row(InlineKeyboardButton(text="Одобрить приглашение",
                                                             callback_data=f"confirm_friend|{application_id}"))
            confirm_friend_keyboard.row(InlineKeyboardButton(text="Отклонить приглашение",
                                                             callback_data=f"not_confirm_friend|{application_id}"))
            admins = await Dormitory(obchaga=obchaga).get_obchaga_admins()
            text_message = f"Вам пришло оповещение! {await users_api.get_initials()} из комнаты"\
                           f" {await users_api.get_room()}"\
                           f" пригласил {data.get('initiels')}"\
                           f" к себе в гости! Примерное время прибытия: {str(data.get('time'))[:-3]}"
            task_list = [asyncio.create_task(bot.send_message(chat_id=user,
                                                              text=text_message,
                                                              reply_markup=confirm_friend_keyboard.as_markup()))
                         for user in list(admins.keys())]
            await asyncio.gather(*task_list)
            text_for_user = (f"Отлично, ваша заявка отправлена коменданту и ждет одобрения! "
                             f"Вы пригласили {data.get('initiels')} к себе в гости! "
                             f"Примерное время прибытия: {str(data.get('time'))[:-3]}")
            await message.answer(text=text_for_user)
            await state.clear()
            await bot.delete_message(chat_id=message.from_user.id, message_id=message_id)
        elif user_code is None:
            await state.clear()
            await bot.delete_message(message_id=message_id, chat_id=message.from_user.id)
            await message.answer("Вы не создали код для подтверждений своих действий!"
                                         " Добавьте его вличном кабинете,"
                                         " чтобы пользоваться разделом!", reply_markup=profile_keyboard)
        else:
            await bot.edit_message_text(text="Ты ввел неправильный код, попробуй еще раз!",
                                        message_id=message_id,
                                        chat_id=message.from_user.id,
                                        reply_markup=cancel_keyboard.as_markup())
    except:
        await bot.delete_message(chat_id=message.from_user.id, message_id=message_id)
        await message.answer("Не удалось отправить твою заявку. Убедись, что ты ввел все свои"
                             " данные о проживании в общежитии!",
                             reply_markup=profile_keyboard)


@call_friends_router.callback_query(Text(text="Отмена❌"), any_state)
async def canceling(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.clear()
    await call.message.answer("Выбери свои дальнейшие действия", reply_markup=profile_keyboard)


@end_router.message(any_state)
async def another(message: types.Message):
    await message.answer('👋Я вас не понимать! Выберите свои дальнейшие действия!',
                         reply_markup=start_keyboard)