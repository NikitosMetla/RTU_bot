import asyncio
import datetime

from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Text
from aiogram.fsm.state import any_state
from aiogram.types import User
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.keyboards import main_admin_keyboard, choise_obchaga, back_to_obchaga, dormitories_keyboard, back_to_graphic, \
    back_choise_obchaga, profile_keyboard
from data.settings import InputMessage
from db.all_dormitories import Dormitory
from db.guests_applications import Guests
from db.students_requests_for_admins import Request
from db.users import Users
from utils.is_main_admin import is_main_admin
from utils.keyboard_floors import Floors

main_admin_router = Router()


@main_admin_router.message(Text(text="/main_admin"), any_state)
@is_main_admin
async def main_admin(message: types.Message, state: FSMContext, bot: Bot):
    await state.clear()
    await message.answer("Привествуем, выберите свои дальнейшие действия!",
                         reply_markup=main_admin_keyboard.as_markup())


@main_admin_router.callback_query(Text(text="main_admin"), any_state)
@is_main_admin
async def main_admin(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    await state.clear()
    await call.message.edit_text("Привествуем, выберите свои дальнейшие действия!",
                                 reply_markup=main_admin_keyboard.as_markup())


@main_admin_router.callback_query(Text(text="post_information"), any_state)
async def post_informaiton(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    await state.clear()
    await call.message.edit_text("Выберете, в каком масштабе будет рассылаться информация!",
                                 reply_markup=choise_obchaga.as_markup())


@main_admin_router.callback_query(Text(startswith="post|obchaga|"), any_state)
async def all_obchaga(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    obchaga = call.data.split("|")[-1]
    if not await Dormitory(obchaga).admin_in_obchaga(call.from_user.id):
        await call.message.edit_text("Вы не являетесь комендантом данного общежития, попробуйте еще раз!")
        await call.message.edit_reply_markup(reply_markup=choise_obchaga.as_markup())
    else:
        await state.set_state(InputMessage.enter_post_information)
        await state.update_data(obchaga=obchaga)
        await call.message.edit_text(text=f"Введите информацию поста, которая разошлется студентам <b>{obchaga}</b>"
                                          f" общежития. Прикрепите фотографию, если нужно!",
                                     reply_markup=back_to_obchaga.as_markup())


@main_admin_router.message(InputMessage.enter_post_information)
async def enter_post(message: types.Message, state: FSMContext, bot: Bot):
    obchaga = await state.get_data()
    obchaga = obchaga.get("obchaga")
    users = await Dormitory(obchaga).get_obchaga_students()
    if message.photo is not None:
        caption = message.caption
        if caption is None:
            caption = ""
        text_message = "<b>Объявление от администрации: </b>\n" + caption
        task_list = [asyncio.create_task(bot.send_photo(chat_id=user, photo=message.photo[-1].file_id,
                                                        caption=text_message)) for user in users]
        await asyncio.gather(*task_list)
    else:
        text_message = "<b>Объявление от администрации: </b>\n" + message.text
        task_list = [asyncio.create_task(bot.send_message(chat_id=user, text=text_message)) for user in users]
        await asyncio.gather(*task_list)
    await message.answer("Ваше объявление отправлено студентам!", reply_markup=main_admin_keyboard.as_markup())
    await state.clear()


@main_admin_router.callback_query(Text(startswith="delete_headman"), any_state)
async def choise_del_headman(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(InputMessage.choise_del_headman)
    await call.message.edit_text("Отлично, выберите Ваше общежитие!!",
                                 reply_markup=dormitories_keyboard.as_markup())


@main_admin_router.callback_query(Text(startswith="obchaga|"), InputMessage.choise_del_headman)
async def del_obhaga_headman(call: types.CallbackQuery, state: FSMContext):
    number_obchaga = call.data.split("|")[1]
    obchaga = Dormitory(obchaga=number_obchaga)
    floors_keyboard = await Floors(number_obchaga).generate_keyboard()
    if await obchaga.admin_in_obchaga(user_id=call.from_user.id):
        await call.message.edit_text("Отлично, выберите номер этажа, старосту которого вы хотите удалить",
                                     reply_markup=floors_keyboard.as_markup())
    else:
        await call.message.edit_text("Вы не являетесь комендантом данного общежития! Попробуйте снова"),
        await call.message.edit_reply_markup(reply_markup=dormitories_keyboard.as_markup())


@main_admin_router.callback_query(Text(startswith="floor|"), InputMessage.choise_del_headman)
async def del_floor_headman(call: types.CallbackQuery, state: FSMContext):
    data = call.data.split("|")[1:]
    floor, obchaga = data[0], data[1]
    keyboard = await Floors(obchaga=obchaga, floor=floor).list_headmans()
    keyboard.row(types.InlineKeyboardButton(text="Назад к выбору этажа", callback_data=f"obchaga|{obchaga}"))
    await call.message.edit_text("Выберите старосту из списка, которого вы хотите удалить",
                                 reply_markup=keyboard.as_markup())


@main_admin_router.callback_query(Text(startswith="del_head|"), InputMessage.choise_del_headman)
async def choise_headman_del(call: types.CallbackQuery, state: FSMContext):
    data = call.data.split("|")[1:]
    obchaga, floor, headman_id = data[0], data[1], data[2]
    initials = await Dormitory(obchaga=obchaga, floor=floor).get_headman()
    initials = initials.get(headman_id)
    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(text="Удалить данного старосту этажа",
                                            callback_data="finally_delete|" + "|".join(data)))
    keyboard.row(types.InlineKeyboardButton(text="Назад к выбору старосты",
                                            callback_data=f"floor|{floor}|{obchaga}"))
    await call.message.edit_text(text=f"Выберите свои дальнейшие действия со старостой <b>{initials}</b>"
                                      f" из {obchaga} общежития с {floor} этажа", reply_markup=keyboard.as_markup())


@main_admin_router.callback_query(Text(startswith="finally_delete|"), InputMessage.choise_del_headman)
async def finally_del_headman(call: types.CallbackQuery, state: FSMContext):
    data = call.data.split("|")[1:]
    obchaga, floor, headman_id = data[0], data[1], data[2]
    initials = await Dormitory(obchaga=obchaga, floor=floor).get_headman()
    initials = initials.get(headman_id)
    await Dormitory(obchaga=obchaga, floor=floor).delete_starosta(headman_id)
    keyboard = await Floors(obchaga=obchaga, floor=floor).list_headmans()
    keyboard.row(types.InlineKeyboardButton(text="Назад к выбору этажа", callback_data=f"obchaga|{obchaga}"))
    await call.message.edit_text("Вы удалили старосту Выберите старосту из списка, которого вы хотите удалить",
                                 reply_markup=keyboard.as_markup())


@main_admin_router.callback_query(Text(startswith="new_admin"), any_state)
async def new_admin(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(InputMessage.enter_admin_ID)
    await state.update_data(message_id=call.message.message_id)
    await call.message.edit_text(text="Выберите общежитие нового коменданта!",
                                 reply_markup=dormitories_keyboard.as_markup())


@main_admin_router.callback_query(Text(startswith="new_admin_obchaga"), InputMessage.enter_admin_ID)
@main_admin_router.callback_query(Text(startswith="obchaga|"), InputMessage.enter_admin_ID)
async def choise_obhaga_admin(call: types.CallbackQuery, state: FSMContext):
    number_obchaga = call.data.split("|")[1]
    obchaga = Dormitory(obchaga=number_obchaga)
    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(text="Назад к выбору действий", callback_data="main_admin"))
    if await obchaga.admin_in_obchaga(user_id=call.from_user.id):
        await call.message.edit_text("Отлично, напишите telegram id нового коменданта!",
                                     reply_markup=keyboard.as_markup())
        await state.update_data(obchaga=number_obchaga)
    else:
        await call.message.edit_text("Вы не являетесь комендантом данного общежития! Попробуйте снова"),
        await call.message.edit_reply_markup(reply_markup=dormitories_keyboard.as_markup())


@main_admin_router.message(F.text, InputMessage.enter_admin_ID)
async def enter_admin_id(message: types.Message, state: FSMContext, bot: Bot):
    admin_id = message.text
    data = await state.get_data()
    message_id = data.get("message_id")
    obchaga = data.get("obchaga")
    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(text="Назад к выбору действий", callback_data="main_admin"))
    if not admin_id.isdigit():
        await bot.edit_message_text(text="Вы ввели несуществующий telegram_id, попробуйте еще раз",
                                    chat_id=message.from_user.id,
                                    message_id=message_id)
        await bot.edit_message_reply_markup(chat_id=message.from_user.id,
                                            message_id=message_id,
                                            reply_markup=keyboard.as_markup())
        await message.delete()
        return
    await bot.edit_message_text("Отлично, введите ФИО нового коменданта!", chat_id=message.from_user.id,
                                message_id=message_id, reply_markup=keyboard.as_markup())
    await message.delete()
    data["admin_id"] = admin_id
    await state.set_state(InputMessage.enter_admin_initials)
    await state.update_data(data)


@main_admin_router.message(F.text, InputMessage.enter_admin_initials)
async def enter_admin_initials(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    initials, message_id, obchaga, admin_id = (message.text, data.get("message_id"),
                                               data.get("obchaga"), data.get("admin_id"))
    await state.clear()


    try:
        dormitory = Dormitory(obchaga=obchaga)
        await dormitory.add_admin(user_id=admin_id, initials=initials)
        await bot.send_message(chat_id=admin_id, text=f"Вас добавили в бота,"
                                                      f" как коменданта {obchaga} общежития!")
        await bot.delete_message(chat_id=message.from_user.id, message_id=message_id)
        keyboard = InlineKeyboardBuilder()
        keyboard.row(types.InlineKeyboardButton(text="Назад к выбору действий", callback_data="main_admin"))
        await message.answer("Отлично, вы добавили нового коменданта!", reply_markup=keyboard.as_markup())
        await state.clear()
    except:
        keyboard = InlineKeyboardBuilder()
        keyboard.row(types.InlineKeyboardButton(text="Назад к выбору этажа", callback_data=f"obchaga|{obchaga}"))
        await bot.edit_message_text("Такого telegram id не существует! Попробуйте еще раз!",
                                    chat_id=message.from_user.id,
                                    message_id=message_id,
                                    reply_markup=keyboard.as_markup())
        await state.set_state(InputMessage.enter_admin_ID)
        await state.update_data(obchaga=obchaga, message_id=message_id)
        await message.delete()


@main_admin_router.callback_query(Text(startswith="new_security"), any_state)
async def new_security(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(InputMessage.new_security)
    await state.update_data(message_id=call.message.message_id)
    await call.message.edit_text(text="Выберите общежитие нового аккаунта охранника!",
                                 reply_markup=dormitories_keyboard.as_markup())


@main_admin_router.callback_query(Text(startswith="obchaga|"), InputMessage.new_security)
async def choise_obhaga_admin(call: types.CallbackQuery, state: FSMContext):
    number_obchaga = call.data.split("|")[1]
    obchaga = Dormitory(obchaga=number_obchaga)
    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(text="Назад к выбору действий", callback_data="main_admin"))
    if await obchaga.admin_in_obchaga(user_id=call.from_user.id):
        await call.message.edit_text("Отлично, напишите telegram id нового аккаунта охранника! Учтите,"
                                     " что на общежитие может быть только один аккаунт telegram для охранника,"
                                     " соответственно, если вы добавите новый telegram id,"
                                     " то старый автоматически удалится!",
                                     reply_markup=keyboard.as_markup())
        await state.set_state(InputMessage.enter_security_ID)
        await state.update_data(obchaga=number_obchaga)
    else:
        await call.message.edit_text("Вы не являетесь комендантом данного общежития! Попробуйте снова"),
        await call.message.edit_reply_markup(reply_markup=dormitories_keyboard.as_markup())


@main_admin_router.message(F.text, InputMessage.enter_security_ID)
async def enter_security_id(message: types.Message, state: FSMContext, bot: Bot):
    security_id = message.text
    data = await state.get_data()
    message_id = data.get("message_id")
    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(text="Назад к выбору действий", callback_data="main_admin"))
    try:
        await bot.send_message(chat_id=security_id, text="Вас добавили в данного бота, как охранника!")
        await Dormitory(obchaga=data.get("obchaga")).add_security(message.text)
        await bot.edit_message_text("Отлично, вы добавили нового охранника с id!", chat_id=message.from_user.id,
                                    message_id=message_id, reply_markup=keyboard.as_markup())
        await message.delete()
        await state.clear()
    except:
        await bot.edit_message_text(text="Вы ввели несуществующий telegram_id, попробуйте еще раз",
                                    chat_id=message.from_user.id,
                                    message_id=message_id)
        await bot.edit_message_reply_markup(chat_id=message.from_user.id,
                                            message_id=message_id,
                                            reply_markup=keyboard.as_markup())
        await message.delete()


@main_admin_router.message(F.text, InputMessage.enter_admin_initials)
async def enter_admin_initials(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    initials, message_id, obchaga, admin_id = (message.text, data.get("message_id"),
                                               data.get("obchaga"), data.get("admin_id"))
    await state.clear()
    try:
        await bot.send_message(chat_id=admin_id, text=f"Вас добавили в бота,"
                                                      f" как коменданта {obchaga} общежития!")
        dormitory = Dormitory(obchaga=obchaga)
        await dormitory.add_admin(user_id=admin_id, initials=initials)
        await bot.delete_message(chat_id=message.from_user.id, message_id=message_id)
        keyboard = InlineKeyboardBuilder()
        keyboard.row(types.InlineKeyboardButton(text="Назад к выбору действий", callback_data="main_admin"))
        await message.answer("Отлично, вы добавили нового коменданта!", reply_markup=keyboard.as_markup())
        await state.clear()
    except:
        keyboard = InlineKeyboardBuilder()
        keyboard.row(types.InlineKeyboardButton(text="Назад к выбору этажа", callback_data=f"obchaga|{obchaga}"))
        await bot.edit_message_text("Такого telegram id не существует! Попробуйте еще раз!",
                                    chat_id=message.from_user.id,
                                    message_id=message_id,
                                    reply_markup=keyboard.as_markup())
        await state.set_state(InputMessage.enter_admin_ID)
        await state.update_data(obchaga=obchaga, message_id=message_id)
        await message.delete()


@main_admin_router.callback_query(Text(text="new_headman"), any_state)
async def add_headman(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Отлично, выберите ваше общежитие!!",
                                 reply_markup=dormitories_keyboard.as_markup())


@main_admin_router.callback_query(Text(startswith="obchaga|"), any_state)
async def choise_obhaga_headman(call: types.CallbackQuery, state: FSMContext):
    number_obchaga = call.data.split("|")[1]
    obchaga = Dormitory(obchaga=number_obchaga)
    floors_keyboard = await Floors(number_obchaga).generate_keyboard()
    if await obchaga.admin_in_obchaga(user_id=call.from_user.id):
        await call.message.edit_text("Отлично, выберите номер этажа для старосты",
                                     reply_markup=floors_keyboard.as_markup())
        await state.set_state(InputMessage.choise_floor_headman)
        await state.update_data(obchaga=number_obchaga)
    else:
        await call.message.edit_text("Вы не являетесь комендантом данного общежития! Попробуйте снова"),
        await call.message.edit_reply_markup(reply_markup=dormitories_keyboard.as_markup())


@main_admin_router.callback_query(Text(startswith="floor|"), any_state)
async def choise_floor_headman(call: types.CallbackQuery, state: FSMContext):
    data = call.data.split("|")[1:]
    floor, obchaga = data[0], data[1]
    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(text="Назад к выбору этажа", callback_data=f"obchaga|{obchaga}"))
    await call.message.edit_text("Отлично, введите telegram ID нового старосты!", reply_markup=keyboard.as_markup())
    await state.set_state(InputMessage.enter_headman_ID)
    await state.update_data(obchaga=obchaga, floor=floor, message_id=call.message.message_id)


@main_admin_router.message(F.text, InputMessage.enter_headman_ID)
async def enter_headman_id(message: types.Message, state: FSMContext, bot: Bot):
    headman_id = message.text
    data = await state.get_data()
    message_id = data.get("message_id")
    keyboard = InlineKeyboardBuilder()
    obchaga = data.get("obchaga")
    keyboard.row(types.InlineKeyboardButton(text="Назад к выбору этажа", callback_data=f"obchaga|{obchaga}"))
    if not headman_id.isdigit():
        await bot.edit_message_text(text="Вы ввели несуществующий telegram_id, попробуйте еще раз",
                                    chat_id=message.from_user.id,
                                    message_id=message_id)
        await bot.edit_message_reply_markup(chat_id=message.from_user.id,
                                            message_id=message_id,
                                            reply_markup=keyboard.as_markup())
        await message.delete()
        return
    await bot.edit_message_text("Отлично, введите ФИО нового старосты!", chat_id=message.from_user.id,
                                message_id=message_id, reply_markup=keyboard.as_markup())
    await message.delete()
    data["headman_id"] = headman_id
    await state.set_state(InputMessage.enter_headman_initials)
    await state.update_data(data)


@main_admin_router.message(F.text, InputMessage.enter_headman_initials)
async def enter_headman_initials(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    initials, message_id, floor, obchaga, headman_id = (message.text, data.get("message_id"), data.get("floor"),
                                                        data.get("obchaga"), data.get("headman_id"))
    await state.clear()
    try:
        await bot.send_message(chat_id=headman_id, text=f"Вас добавили в бота,"
                                                        f" как сторосту {obchaga} общежития {floor} этажа")
        dormitory = Dormitory(obchaga=obchaga, floor=floor)
        await dormitory.add_starosta(user_id=headman_id, initials=initials)
        await bot.delete_message(chat_id=message.from_user.id, message_id=message_id)
        keyboard = InlineKeyboardBuilder()
        keyboard.row(types.InlineKeyboardButton(text="Назад к выбору действий", callback_data="main_admin"))
        await message.answer("Отлично, вы добавили нового старосту!", reply_markup=keyboard.as_markup())
        await state.clear()
    except:
        keyboard = InlineKeyboardBuilder()
        keyboard.row(types.InlineKeyboardButton(text="Назад к выбору этажа", callback_data=f"obchaga|{obchaga}"))
        await bot.edit_message_text("Такого telegram id не существует! Попробуйте еще раз!",
                                    chat_id=message.from_user.id,
                                    message_id=message_id,
                                    reply_markup=keyboard.as_markup())
        await state.set_state(InputMessage.enter_headman_ID)
        await state.update_data(obchaga=obchaga, floor=floor, message_id=message_id)
        await message.delete()


@main_admin_router.callback_query(Text(startswith="confirm_friend|"), any_state)
async def confirm_guests(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    data = call.data.split("|")[1:]
    application_id = "|".join(data)
    guests = Guests(user_id=data[0], application_id=application_id)
    await guests.edit_cofirm_guests()
    user_id, friend_initials, time = data[0], await guests.get_friends_initials(), await guests.get_time()
    users_api = Users(str(user_id))
    obchaga = await users_api.get_number_of_obchaga()
    text_message = f"Вам пришло оповещение! {await users_api.get_initials()} из комнаты" \
                   f" {await users_api.get_room()}" \
                   f" пригласил {friend_initials}" \
                   f" к себе в гости! Примерное время прибытия: {time[:-3]}"
    print(await Dormitory(obchaga=obchaga).get_obchaga_security())
    await bot.send_message(chat_id=await Dormitory(obchaga=obchaga).get_obchaga_security(), text=text_message)
    await bot.send_message(text=f"Ваша заявка одобрена! "       
                                f"Вы пригласили {friend_initials} к себе в гости!"
                                f" Примерное время прибытия: {time  [:-3]}",
                           chat_id=user_id,
                           reply_markup=profile_keyboard)
    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(text="К выбору дальнейших действий",
                                            callback_data="main_admin"))
    await call.message.edit_reply_markup(reply_markup=keyboard.as_markup())


@main_admin_router.callback_query(Text(startswith="not_confirm_friend|"), any_state)
async def not_confirm_guests(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    data = call.data.split("|")[1:]
    application_id = "|".join(data)
    guests = Guests(user_id=data[0], application_id=application_id)
    user_id, friend_initials, time = data[0], await guests.get_friends_initials(), await guests.get_time()
    await guests.delete_guests()
    users_api = Users(str(user_id))
    await bot.send_message(text=f"Ваша заявка, когда "       
                                f"вы пригласили {friend_initials} к себе в гости"
                                f" к {time  [:-3]} - <b>НЕ ОДОБРЕНА</b>! Просьба, обратится с этим"
                                f" вопросом к коменданту через бота или очно",
                           chat_id=user_id,
                           reply_markup=profile_keyboard)
    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(text="К выбору дальнейших действий",
                                            callback_data="main_admin"))
    await call.message.edit_reply_markup(reply_markup=keyboard.as_markup())


@main_admin_router.callback_query(Text(startswith="accept_processing|"), any_state)
@is_main_admin
async def accept_student_request(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    data = call.data.split("|")[1:]
    obchaga, request_id = data[0], data[1]
    request = Request(obchaga=obchaga)
    datetime_now = str(datetime.datetime.now())
    messages_ids = await request.get_messages_for_admins(request_id=request_id)
    await request.add_date_treatment(date=datetime_now, request_id=request_id)
    await request.edit_request_processing(request_id=request_id, admin_id=call.from_user.id, obchaga=obchaga)
    text_message = await request.get_request_text(request_id=request_id)
    text_message = text_message.split("\n")
    text_message.append(f"<i>Принято в обработку:</i> <b>{datetime_now[:-7]}</b>")
    keyboard_for_admins = InlineKeyboardBuilder()
    keyboard_for_admins.row(types.InlineKeyboardButton(text="Назад к выбору действий", callback_data="main_admin"))
    keyboard_admin = InlineKeyboardBuilder()
    keyboard_admin.row(types.InlineKeyboardButton(text="Объявить готовность",
                                                  callback_data=f"declare_readiness|{obchaga}|{request_id}"))
    if call.message.photo is None:
        await call.message.edit_text(text="\n".join(text_message))
        task_list = [asyncio.create_task(bot.edit_message_text(chat_id=admin, message_id=messages_ids.get(admin),
                                                               text="\n".join(text_message),
                                                               reply_markup=keyboard_for_admins.as_markup()))
                     for admin in messages_ids.keys()]
        await asyncio.gather(*task_list)
    else:
        await call.message.edit_caption(caption="\n".join(text_message))
        task_list = [asyncio.create_task(bot.edit_message_caption(chat_id=admin, message_id=messages_ids.get(admin),
                                                                  caption="\n".join(text_message),
                                                                  reply_markup=keyboard_for_admins.as_markup()))
                     for admin in messages_ids.keys()]
        await asyncio.gather(*task_list)
    await call.message.edit_reply_markup(reply_markup=keyboard_admin.as_markup())


@main_admin_router.callback_query(Text(startswith="declare_readiness|"), any_state)
@is_main_admin
async def processing_student_request(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    call_data = call.data.split("|")[1:]
    obchaga, request_id = call_data[0], call_data[1]
    request = Request(obchaga=obchaga)
    datetime_now = str(datetime.datetime.now())
    messages_ids = await request.get_messages_for_admins(request_id=request_id)
    if call.message.photo is None:
        text_message = call.message.text
    else:
        text_message = call.message.caption
    text_message = text_message.split("\n")
    text_message.append(f"<i>Объявлена готовность:</i> <b>{datetime_now[:-7]}</b>")
    await request.edit_request_text(request_id=request_id, request_text="\n".join(text_message))
    if call.message.photo is None:
        task_list = [asyncio.create_task(bot.edit_message_text(chat_id=admin,
                                                               message_id=messages_ids.get(admin),
                                                               text="\n".join(text_message)))
                     for admin in messages_ids.keys()]
        await asyncio.gather(*task_list)
        await call.message.edit_text(text="\n".join(text_message))
        data = {"obchaga": obchaga, "request_id": request_id, "message_id": call.message.message_id, "photo": False}
    else:
        task_list = [asyncio.create_task(bot.edit_message_caption(chat_id=admin,
                                                                  message_id=messages_ids.get(admin),
                                                                  caption="\n".join(text_message)))
                     for admin in messages_ids.keys()]
        await asyncio.gather(*task_list)
        await call.message.edit_caption(caption="\n".join(text_message))
        data = {"obchaga": obchaga, "request_id": request_id, "message_id": call.message.message_id, "photo": True}
    await state.set_state(InputMessage.enter_comment_request)
    await state.update_data(data=data)
    await call.message.answer(text="Введите ваш комментарий к данной заявке!")


@main_admin_router.message(F.text, InputMessage.enter_comment_request)
@is_main_admin
async def accept_student_request(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    obchaga, request_id, message_id = data.get("obchaga"), data.get("request_id"), data.get("message_id")
    request = Request(obchaga=obchaga)
    text_for_student = message.text
    await message.delete()
    text_message = await request.get_request_text(request_id=request_id)
    text_message = text_message.split("\n")
    text_message.append("<i>Ответ коменданта:</i>\n" + text_for_student)
    await request.add_admin_text(request_id=request_id, admin_text=text_for_student)
    student_id = await request.get_request_student_id(request_id=request_id)
    await bot.send_message(text=f"По вашей заявке №{request_id} была объевлена готовность!"
                                f" <b>Ответ коменданта:</b>\n {text_for_student}", chat_id=student_id,
                           reply_markup=profile_keyboard)
    messages_ids = await request.get_messages_for_admins(request_id=request_id)
    if not data.get("photo"):
        task_list = [asyncio.create_task(bot.edit_message_text(chat_id=admin,
                                                               message_id=messages_ids.get(admin),
                                                               text="\n".join(text_message)))
                     for admin in messages_ids.keys()]
        await asyncio.gather(*task_list)
        await bot.edit_message_text(chat_id=message.from_user.id, message_id=message_id, text="\n".join(text_message))
    else:
        task_list = [asyncio.create_task(bot.edit_message_caption(chat_id=admin,
                                                                  message_id=messages_ids.get(admin),
                                                                  caption="\n".join(text_message)))
                     for admin in messages_ids.keys()]
        await asyncio.gather(*task_list)
        await bot.edit_message_caption(chat_id=message.from_user.id, message_id=message_id,
                                       caption="\n".join(text_message))
    await request.announce_acceptance(request_id)
    await state.clear()



