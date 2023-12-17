from aiogram import Bot, types, F
from aiogram import Router
from aiogram.filters import Command, Text, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import any_state
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.keyboards import profile_keyboard, start_keyboard, check_in_cleaning, cancel_keyboard, categories_keyboard, \
    buy_or_sell_keyboard, restore_keyboard
from db.user_things import Things
from db.users import Users
from utils.is_auth import is_auth
from utils.paginator import Paginator
from utils.data_of_thing import CreateThing

from data.settings import (InputMessage, develop_ids, comendant_ids,
                           categories, moderators)
import datetime


# router = Router()
# end_router = Router()


# @router.message(CommandStart(), any_state)
# @is_auth
# async def start(message: types.Message, state: FSMContext):
#     await state.clear()
#     await message.delete()
#     user_data = Users(user_id=message.from_user.id)
#     if await user_data.get_auth():
#         return await message.answer('<b>👋Привет, ты успешно авторизирован! Выбери свои дальнейшие действия!</b>',
#                                     reply_markup=profile_keyboard)
#
#
# @router.message(Text(text='Авторизация', ignore_case=True))
# async def auth_user(message: types.Message, state: FSMContext):
#     user_data = Users(user_id=message.from_user.id)
#     if await user_data.get_auth():
#         return message.answer('<b>Вы уже авторизированы в системе</b>', reply_markup=profile_keyboard)
#     await message.answer('<b>Для авторизации, следуйте дальнейшим действиям, что просит от вас бот:\n'
#                          'Пришлите email в виде: login@edu.mirea.ru</b>')
#     await state.set_state(InputMessage.input_email)


# @router.message(Text(text="График уборкиℹ️", ignore_case=True))
# async def help_to_student(message: types.Message, state: FSMContext):
#
#     await message.reply("Выберите свои дальнейшие действия!", reply_markup=check_in_cleaning.as_markup())
#
#
# @router.callback_query(Text(contains="Посмотреть свой график📅"), any_state)
# async def answer_to_user(call: types.CallbackQuery, state: FSMContext):
#     await call.message.reply(f"<b>Вы выбрали просмотр своего графика:</b>\n"
#                              f"<i>День недели:</i> Четверг\n<i>Время</i>: 14:00-16:00\n"
#                              f"<i>Место проведения:</i> Общежитие №1, 2 этаж"
#                              f"\n<b><i>Если вы хотите изменить график,"
#                              f" обратитесь к коменданту через бота или очно</i></b>",
#                              reply_markup=profile_keyboard)
#
#
# @router.callback_query(Text(contains="Начать уборку▶️"), any_state)
# async def answer_to_user(call: types.CallbackQuery, state: FSMContext):
#     keyboard = InlineKeyboardBuilder()
#     keyboard.row(InlineKeyboardButton(text="Завершить уборку☑️", callback_data="end_cleaning"))
#     await call.message.reply(f"Вы начали уборку, коменданту пришло уведомление об этом.\n"
#                              f"Нажмите кнопку, когда закончите убираться!",
#                              reply_markup=keyboard.as_markup())
#
#
# @router.callback_query(Text(text="end_cleaning"), any_state)
# async def answer_to_user(call: types.CallbackQuery, state: FSMContext):
#     restore_kb = [
#         [types.KeyboardButton(text="Да"), types.KeyboardButton(text="Нет")]
#     ]
#     keyboard = types.ReplyKeyboardMarkup(keyboard=restore_kb, resize_keyboard=True)
#     await call.message.reply("Вы уверены, что хотите закончить уборку?", reply_markup=keyboard)
#
#
# @router.message(Text(text="Да"), any_state)
# async def answer_to_user(message: types.Message, state: FSMContext):
#     await message.reply(f"Отлично, коменданту пришло уведомление о завершении уборки!"
#                         f" В ближайшее время он подойдет на место и проведет проверку",
#                         reply_markup=profile_keyboard)
#
#
# @router.message(Text(text="Связь с разработчиками💬", ignore_case=True))
# async def help_to_student(message: types.Message, state: FSMContext):
#     await state.set_state(InputMessage.message_to_developer)
#     await message.reply("Напишите какой вопрос или предложение вы хотите написать", reply_markup=cancel_keyboard)
#
#
# @router.message(Text(text="Отмена❌", ignore_case=True), any_state)
# async def help_to_student(message: types.Message, state: FSMContext):
#     await state.clear()
#     await message.reply("Выбери свои дальнейшие действия", reply_markup=profile_keyboard)
#
#
# @router.message(InputMessage.message_to_developer)
# async def listening_of_question(message: types.Message, state: FSMContext, bot: Bot):
#     keyboard_for_develop = InlineKeyboardBuilder()
#     keyboard_for_develop.row(InlineKeyboardButton(text=f"Ответить пользователю?",
#                                                   callback_data=f"Ответить пользователю {message.from_user.id}"))
#     keyboard_for_develop.row(InlineKeyboardButton(text="Игнорировать", callback_data="No"))
#     if message.photo is not None:
#         text_message = "<b>Сообщение от пользователя: </b>" + message.caption + "\n" + \
#                        f"user_id: {message.from_user.id}" + "\nХотите ответить пользователю?"
#         await bot.send_photo(chat_id=develop_ids[0], photo=message.photo[-1].file_id, caption=text_message,
#                              reply_markup=keyboard_for_develop.as_markup())
#     else:
#         text_message = "<b>Сообщение от пользователя: </b>" + message.text + "\n" + \
#                        f"user_id: {message.from_user.id}" + "\nХотите ответить пользователю?"
#         await bot.send_message(chat_id=develop_ids[0], text=text_message, reply_markup=keyboard_for_develop.as_markup())
#     await message.reply("Твой запрос отправлен разработчику!", reply_markup=profile_keyboard)
#     await state.clear()


# @router.message(Text(text="Связь с комендантом💬", ignore_case=True))
# async def visit_friend(message: types.Message, state: FSMContext):
#     await message.reply("Отлично, отправь свой вопрос или просьбу!",
#                         reply_markup=cancel_keyboard)
#     await state.set_state(InputMessage.message_to_comendant)
#
#
# @router.message(InputMessage.message_to_comendant)
# async def visit_friend(message: types.Message, state: FSMContext, bot: Bot):
#     users_api = Users(message.from_user.id)
#     keyboard_for_comendant = InlineKeyboardBuilder()
#     keyboard_for_comendant.row(InlineKeyboardButton(text=f"Ответить студенту?",
#                                                     callback_data=f"id {message.from_user.id}"))
#     keyboard_for_comendant.row(InlineKeyboardButton(text="Игнорировать", callback_data="No"))
#     if message.photo is None:
#         await bot.send_message(chat_id=comendant_ids.get(await users_api.get_number_of_obchaga()).get(await users_api.get_floor()),
#                                text=f"Вам пришло сообщение от {await users_api.get_initials()}"
#                                     f" из комнаты {await users_api.get_room()}:\n{message.text}",
#                                reply_markup=keyboard_for_comendant.as_markup())
#         await message.reply("Ваше сообщение отправлено коменданту!", reply_markup=profile_keyboard)
#     else:
#         await bot.send_photo(chat_id=comendant_ids.get(await users_api.get_number_of_obchaga()).get(await users_api.get_floor()),
#                              caption=f"Вам пришло сообщение от {await users_api.get_initials()}"
#                                      f" из комнаты {await users_api.get_room()}:\n{message.caption}",
#                              photo=message.photo[-1].file_id,
#                              reply_markup=keyboard_for_comendant.as_markup())
#         await message.reply("Ваше сообщение отправлено коменданту!", reply_markup=profile_keyboard)


# @router.callback_query(Text(contains="Отмена❌|"), any_state)
# async def answer_to_user(call: types.CallbackQuery, state: FSMContext):
#     await call.message.delete()
#     await state.clear()
#     data = call.data.split("|")[1:]
#     thing = Things(category=data[0], user_id=data[1], thing_id=data[2])
#     await thing.delete_thing()
#     await call.message.answer("Выбери свои дальнейшие действия", reply_markup=profile_keyboard)


# @router.message(Text(text="Барахолка💵", ignore_case=True), any_state)
# async def visit_friend(message: types.Message, state: FSMContext):
#     await message.reply("Отлично, выбери свои дальнейшие действия!",
#                         reply_markup=buy_or_sell_keyboard)
#     # await state.set_state(InputMessage.choice_category)
#
#
# @router.message(Text(text="Продать💰", ignore_case=True))
# async def visit_friend(message: types.Message, state: FSMContext):
#     await state.set_state(InputMessage.enter_category)
#     await message.answer("Выберите категорию своего товара!", reply_markup=categories_keyboard.as_markup())
#
#
# @router.callback_query(lambda call: call.data in categories and call.data != "Отмена❌", InputMessage.enter_category)
# async def answer_to_user(call: types.CallbackQuery, state: FSMContext):
#     thing = Things(category=call.data)
#     await thing.add_thing(user_id=call.from_user.id)
#     # print(call.from_user.id)
#     thing_id = thing.thing_id
#     print(call.data, call.from_user.id, thing_id)
#     keyboard = CreateThing(category=call.data, user_id=call.from_user.id, thing_id=thing_id)
#     keyboard = await keyboard.data_thing_keyboard()
#     keyboard.row(InlineKeyboardButton(text="Отмена❌", callback_data=f"Отмена❌|{thing.category}|"
#                                                                     f"{thing.user_id}|{thing.thing_id}"))
#     await call.message.edit_text(f"Твое объявление:\n"
#                                  f"Категория: {thing.category}\n"
#                                  f"Название вещи: {await thing.get_name()}\n"
#                                  f"Цена: {await thing.get_price()}\n"
#                                  f"Состояние: {await thing.get_state_thing()}\n"
#                                  f"Описание: {await thing.get_description()}\n"
#                                  f"Фотографии:", reply_markup=keyboard.as_markup())
#     await state.clear()
#
#
# @router.callback_query(Text(contains="name"), any_state)
# async def enter_name(call: types.CallbackQuery, state: FSMContext):
#     data = call.data.split("|")
#     data = "|".join(data[1:])
#     await state.set_state(InputMessage.enter_name)
#     await state.update_data(thing=data)
#     await call.message.edit_text("Введите название вещи")
#
#
# @router.message(F.text, InputMessage.enter_name)
# async def enter_name(message: types.Message, state: FSMContext):
#     data = await state.get_data()
#     await state.clear()
#     data = data.get("thing").split("|")
#     category = data[0]
#     user_id = data[1]
#     thing_id = data[2]
#     thing = Things(category=category, user_id=user_id, thing_id=thing_id)
#     keyboard = CreateThing(category=category, user_id=message.from_user.id, thing_id=thing_id)
#     keyboard = await keyboard.data_thing_keyboard()
#     keyboard.row(InlineKeyboardButton(text="Отмена❌", callback_data=f"Отмена❌|{thing.category}|"
#                                                                    f"{thing.user_id}|{thing.thing_id}"))
#     await thing.edit_name(message.text)
#     await message.reply(text=f"Твое объявление:\n"
#                              f"Категория: {category}\n"
#                              f"Название вещи: {await thing.get_name()}\n"
#                              f"Цена: {await thing.get_price()}\n"
#                              f"Состояние: {await thing.get_state_thing()}\n"
#                              f"Описание: {await thing.get_description()}\n"
#                              f"Фотографии:", reply_markup=keyboard.as_markup())
#
#
# @router.callback_query(Text(contains="price"), any_state)
# async def enter_name(call: types.CallbackQuery, state: FSMContext):
#     data = call.data.split("|")
#     data = "|".join(data[1:])
#     await state.set_state(InputMessage.enter_price)
#     await state.update_data(thing=data)
#     await call.message.edit_text("Введите цену товара")
#
#
# @router.message(F.text, InputMessage.enter_price)
# async def enter_name(message: types.Message, state: FSMContext):
#     data = await state.get_data()
#     await state.clear()
#     data = data.get("thing").split("|")
#     category = data[0]
#     user_id = data[1]
#     thing_id = data[2]
#     thing = Things(category=category, user_id=user_id, thing_id=thing_id)
#     keyboard = CreateThing(category=category, user_id=message.from_user.id, thing_id=thing_id)
#     keyboard = await keyboard.data_thing_keyboard()
#     keyboard.row(InlineKeyboardButton(text="Отмена❌", callback_data=f"Отмена❌|{thing.category}|"
#                                                                    f"{thing.user_id}|{thing.thing_id}"))
#     await thing.edit_price(message.text)
#     await message.reply(text=f"Твое объявление:\n"
#                              f"Категория: {category}\n"
#                              f"Название вещи: {await thing.get_name()}\n"
#                              f"Цена: {await thing.get_price()}\n"
#                              f"Состояние: {await thing.get_state_thing()}\n"
#                              f"Описание: {await thing.get_description()}\n"
#                              f"Фотографии:", reply_markup=keyboard.as_markup())
#
#
# @router.callback_query(Text(contains="state"), any_state)
# async def enter_name(call: types.CallbackQuery, state: FSMContext):
#     data = call.data.split("|")
#     data = "|".join(data[1:])
#     await state.set_state(InputMessage.enter_state)
#     await state.update_data(thing=data)
#     await call.message.edit_text("Введите состояние вещи")
#
#
# @router.message(F.text, InputMessage.enter_state)
# async def enter_name(message: types.Message, state: FSMContext):
#     data = await state.get_data()
#     await state.clear()
#     data = data.get("thing").split("|")
#     category = data[0]
#     user_id = data[1]
#     thing_id = data[2]
#     thing = Things(category=category, user_id=user_id, thing_id=thing_id)
#     keyboard = CreateThing(category=category, user_id=message.from_user.id, thing_id=thing_id)
#     keyboard = await keyboard.data_thing_keyboard()
#     keyboard.row(InlineKeyboardButton(text="Отмена❌", callback_data=f"Отмена❌|{thing.category}|"
#                                                                    f"{thing.user_id}|{thing.thing_id}"))
#     await thing.edit_state_thing(message.text)
#     await message.reply(text=f"Твое объявление:\n"
#                              f"Категория: {category}\n"
#                              f"Название вещи: {await thing.get_name()}\n"
#                              f"Цена: {await thing.get_price()}\n"
#                              f"Состояние: {await thing.get_state_thing()}\n"
#                              f"Описание: {await thing.get_description()}\n"
#                              f"Фотографии:", reply_markup=keyboard.as_markup())
#
#
# @router.callback_query(Text(contains="description"), any_state)
# async def enter_name(call: types.CallbackQuery, state: FSMContext):
#     data = call.data.split("|")
#     data = "|".join(data[1:])
#     await state.set_state(InputMessage.enter_description)
#     await state.update_data(thing=data)
#     await call.message.edit_text("Введите описание вещи")
#
#
# @router.message(F.text, InputMessage.enter_description)
# async def enter_name(message: types.Message, state: FSMContext):
#     data = await state.get_data()
#     await state.clear()
#     data = data.get("thing").split("|")
#     category = data[0]
#     user_id = data[1]
#     thing_id = data[2]
#     thing = Things(category=category, user_id=user_id, thing_id=thing_id)
#     keyboard = CreateThing(category=category, user_id=message.from_user.id, thing_id=thing_id)
#     keyboard = await keyboard.data_thing_keyboard()
#     keyboard.row(InlineKeyboardButton(text="Отмена❌", callback_data=f"Отмена❌|{thing.category}|"
#                                                                    f"{thing.user_id}|{thing.thing_id}"))
#     await thing.edit_description(message.text)
#     await message.reply(text=f"Твое объявление:\n"
#                              f"Категория: {category}\n"
#                              f"Название вещи: {await thing.get_name()}\n"
#                              f"Цена: {await thing.get_price()}\n"
#                              f"Состояние: {await thing.get_state_thing()}\n"
#                              f"Описание: {await thing.get_description()}\n"
#                              f"Фотографии:", reply_markup=keyboard.as_markup())


# @router.message(Text(text="Мои объявления🟢"), any_state)
# async def answer_to_user(message: types.Message, state: FSMContext):
#     keyboard = await Paginator().generate_my_things_keyboard(message.from_user.id)
#     await message.answer("Мои объявления из всех категорий:", reply_markup=keyboard.as_markup())
#
#
# @router.callback_query(Text(contains="my_thing|"), any_state)
# async def getting_thing(call: types.CallbackQuery, state: FSMContext):
#     data = call.data.split("|")
#     user_id = data[2]
#     thing_id = data[1]
#     category = data[3]
#     thing = Things(category=category, user_id=user_id, thing_id=thing_id)
#     keyboard = await CreateThing(category=category, user_id=user_id, thing_id=thing_id).edit_thing_keyboard()
#     if not (await thing.get_verified()):
#         keyboard.row(InlineKeyboardButton(text="Отправить на модерацию", callback_data=f"Отправить|{category}|"
#                                                                                        f"{user_id}|{thing_id}"))
#     await call.message.edit_text(f"Название: {await thing.get_name()}\n"
#                                  f"Состояние: {await thing.get_state_thing()}\n"
#                                  f"Цена: {await thing.get_price()}\n"
#                                  f"Описание: {await thing.get_description()}",
#                                  reply_markup=keyboard.as_markup())
#
#
# @router.callback_query(Text(text="back_to_things"), any_state)
# async def next_page(call: types.CallbackQuery, state: FSMContext):
#     keyboard = await Paginator().generate_my_things_keyboard(call.from_user.id)
#     await call.message.edit_text("Мои объявления из всех категорий:", reply_markup=keyboard.as_markup())
#
#
# @router.callback_query(Text(startswith="my_things"), any_state)
# async def next_page(call: types.CallbackQuery, state: FSMContext):
#     data = call.data.split("|")
#     number_page = int(data[2])
#     next_or_back = data[1]
#     if next_or_back == "page_next":
#         number_page += 1
#     else:
#         if number_page != 0:
#             number_page -= 1
#     keyboard = await Paginator().generate_my_things_keyboard(user_id=call.from_user.id, page=number_page)
#     await call.message.edit_text("Мои объявления из всех категорий:", reply_markup=keyboard.as_markup())
#
#
# @router.callback_query(Text(contains="edit_thing"), any_state)
# async def answer_to_user(call: types.CallbackQuery, state: FSMContext):
#     data = call.data.split("|")[1:]
#     category, user_id, thing_id = data[0], data[1], data[2]
#     keyboard = CreateThing(category=category, user_id=user_id, thing_id=thing_id)
#     keyboard = await keyboard.data_thing_keyboard()
#     thing = Things(category=category, user_id=user_id, thing_id=thing_id)
#     keyboard.row(InlineKeyboardButton(text="🔙Назад к моим объявлениям", callback_data="back_to_things"))
#     await thing.edit_verified(False)
#     await call.message.edit_text(f"Твое объявление:\n"
#                                  f"Категория: {category}\n"
#                                  f"Название вещи: {await thing.get_name()}\n"
#                                  f"Цена: {await thing.get_price()}\n"
#                                  f"Состояние: {await thing.get_state_thing()}\n"
#                                  f"Описание: {await thing.get_description()}\n"
#                                  f"Фотографии:",
#                                  reply_markup=keyboard.as_markup())
#
#
# @router.callback_query(Text(contains="delete_thing|"), any_state)
# async def enter_name(call: types.CallbackQuery, state: FSMContext):
#     data = call.data.split("|")[1:]
#     confirm_action = InlineKeyboardBuilder()
#     confirm_action.row(InlineKeyboardButton(text=f"Да", callback_data=f"DELETE|{'|'.join(data)}"))
#     confirm_action.row(InlineKeyboardButton(text=f"Нет", callback_data=f"NOT_DELETE|{'|'.join(data)}"))
#     await call.message.edit_text("Вы уверены, что хотите удалить объявление?", reply_markup=confirm_action.as_markup())
#
#
# @router.callback_query(Text(startswith="DELETE|"), any_state)
# async def enter_name(call: types.CallbackQuery, state: FSMContext):
#     data = call.data.split("|")[1:]
#     thing = await Things(category=data[0], user_id=data[1], thing_id=data[2]).delete_thing()
#     await call.message.edit_text("Ваше объявление было удалено!")
#     keyboard = await Paginator().generate_my_things_keyboard(call.from_user.id)
#     await call.message.answer("Выши объявления:", reply_markup=keyboard.as_markup())
#
#
# @router.callback_query(Text(contains="NOT_DELETE|"), any_state)
# async def enter_name(call: types.CallbackQuery, state: FSMContext):
#     keyboard = await Paginator().generate_my_things_keyboard(call.from_user.id)
#     await call.message.edit_text("Ваши объявления:", reply_markup=keyboard.as_markup())
#
#
# @router.callback_query(Text(contains="Отправить|"), any_state)
# async def enter_name(call: types.CallbackQuery, state: FSMContext):
#     data = call.data.split("|")[1:]
#     thing = Things(category=data[0], user_id=data[1], thing_id=data[2])
#     confirm_action = InlineKeyboardBuilder()
#     confirm_action.row(InlineKeyboardButton(text=f"Да", callback_data=f"MODER|{'|'.join(data)}"))
#     confirm_action.row(InlineKeyboardButton(text=f"Нет", callback_data=f"NOT_MODER|{'|'.join(data)}"))
#     await call.message.edit_text("Вы уверены, что хотите выложить объявление?", reply_markup=confirm_action.as_markup())
#
#
# @router.callback_query(Text(startswith="MODER|"), any_state)
# async def enter_name(call: types.CallbackQuery, state: FSMContext, bot: Bot):
#     data = call.data.split("|")[1:]
#     thing = Things(category=data[0], user_id=data[1], thing_id=data[2])
#     keyboard = InlineKeyboardBuilder()
#     keyboard.row(InlineKeyboardButton(text=f"Одобрить", callback_data=f"APPROVE|{'|'.join(data)}"))
#     keyboard.row(InlineKeyboardButton(text=f"Отменить одобрение", callback_data=f"NOT_APPROVE|{'|'.join(data)}"))
#     await bot.send_message(moderators[0], f"Вам пришло новое объявление!\nНазвание: {await thing.get_name()}\n"
#                                                f"Состояние: {await thing.get_state_thing()}\n"
#                                                f"Цена: {await thing.get_price()}\n"
#                                                f"Описание: {await thing.get_description()}",
#                            reply_markup=keyboard.as_markup())
#     await call.message.delete()
#     await call.message.answer("Ваше объявление отправлено на модерацию!", reply_markup=profile_keyboard)
#
#
# @router.callback_query(Text(startswith="APPROVE|"), any_state)
# async def enter_name(call: types.CallbackQuery, state: FSMContext, bot: Bot):
#     data = call.data.split("|")[1:]
#     thing = Things(category=data[0], user_id=data[1], thing_id=data[2])
#     await thing.edit_verified(True)
#     await call.message.edit_text("Отлично, вы одобрили заявку!")
#     await bot.send_message(chat_id=thing.user_id, text=f"Ваше объявление <b>{await thing.get_name()}</b>"
#                                                        f" одобрено модератором и доступно к просмотру!")
#
#
# @router.callback_query(Text(contains="NOT_MODER|"), any_state)
# async def enter_name(call: types.CallbackQuery, state: FSMContext):
#     keyboard = await Paginator().generate_my_things_keyboard(call.from_user.id)
#     await call.message.edit_text("Выши объявления:", reply_markup=keyboard.as_markup())
#
#
# @router.callback_query(Text(startswith="NOT_APPROVE|"), any_state)
# async def enter_name(call: types.CallbackQuery, state: FSMContext):
#     await state.set_state(InputMessage.comment_to_thing)
#     data = call.data.split("|")[1:]
#     await state.update_data(data="|".join(data))
#     thing = Things(category=data[0], user_id=data[1], thing_id=data[2])
#     await thing.edit_verified(False)
#     await call.message.edit_text("Напишите комментарий, почему вы не одобрили заявку!")
#
#
# @router.message(F.text, InputMessage.comment_to_thing)
# async def answer_to_user(message: types.Message, state: FSMContext, bot: Bot):
#     data = await state.get_data()
#     data = data.get("data").split("|")
#     user_id = data[1]
#     thing = Things(category=data[0], user_id=data[1], thing_id=data[2])
#     text = f"Ваша заявка на публикацию вещи {await thing.get_name()} не одобрена.Комментарий модератора:\n{message.text}"
#     await bot.send_message(chat_id=user_id, text=text)
#     await state.clear()

#
# @router.callback_query(Text(contains="get_categories"), any_state)
# @router.message(Text(text="Посмотреть объявленияℹ📋", ignore_case=True), any_state)
# async def visit_friend(message: types.Message or types.CallbackQuery, state: FSMContext):
#     if type(message) == types.Message:
#         gayboard = categories_keyboard
#         # categories_keyboard.row(InlineKeyboardButton(text="Отмена❌", callback_data="Отмена❌"))
#         await message.answer("Отлично, выбери категорию для просмотра!", reply_markup=gayboard.as_markup())
#         return
#     await message.message.edit_text("Отлично, выбери категорию для просмотра!",
#                                     reply_markup=categories_keyboard.as_markup())
#     # await state.set_state(InputMessage.choice_category)
#
#
# @router.callback_query(Text(text="Отмена❌"), any_state)
# async def answer_to_user(call: types.CallbackQuery, state: FSMContext):
#     await call.message.delete()
#     await state.clear()
#     await call.message.answer("Выбери свои дальнейшие действия", reply_markup=profile_keyboard)
#
#
# @router.callback_query(lambda call: call.data in categories and call.data != "Отмена❌", any_state)
# async def answer_to_user(call: types.CallbackQuery, state: FSMContext):
#     things = Paginator(Things(call.data).user_things.get(call.data), call.data)
#     keyboard = await things.generate_things_list_keyboard()
#     await call.message.edit_text(f"Объявления из категории {call.data}:")
#     await call.message.edit_reply_markup(reply_markup=keyboard.as_markup())
#
#
# @router.callback_query(Text(contains="get_thing"), any_state)
# async def getting_thing(call: types.CallbackQuery, state: FSMContext):
#     data = call.data.split("|")
#     user_id = data[2]
#     thing_id = data[1]
#     category = data[3]
#     thing = Things(category=category, user_id=user_id, thing_id=thing_id)
#     back_to_categories = InlineKeyboardBuilder()
#     back_to_categories.row(InlineKeyboardButton(text="Связаться с продавцом", callback_data="communicate_salesman|"
#                                                                                             + "|".join(data[1:])))
#     back_to_categories.row(InlineKeyboardButton(text="🔙Назад к объявлениям", callback_data=category))
#     await call.message.edit_text(f"Название: {await thing.get_name()}\n"
#                                  f"Состояние: {await thing.get_state_thing()}\n"
#                                  f"Цена: {await thing.get_price()}\n"
#                                  f"Описание: {await thing.get_description()}",
#                                  reply_markup=back_to_categories.as_markup())
#
#
# @router.callback_query(Text(startswith="communicate_salesman"), any_state)
# async def answer_to_user(call: types.CallbackQuery, state: FSMContext):
#     data = call.data.split("|")
#     user_id = data[2]
#     thing_id = data[1]
#     category = data[3]
#     thing = Things(category=category, user_id=user_id, thing_id=thing_id)
#     back_to_categories = InlineKeyboardBuilder()
#     back_to_categories.row(InlineKeyboardButton(text="🔙Назад к объявлениям", callback_data=category))
#     await call.message.edit_text(f"Название: {await thing.get_name()}\n"
#                                  f"Состояние: {await thing.get_state_thing()}\n"
#                                  f"Цена: {await thing.get_price()}\n"
#                                  f"Описание: {await thing.get_description()}\n"
#                                  f"Ссылка на продавца {call.from_user.url}",
#                                  reply_markup=back_to_categories.as_markup())
#
#
# @router.callback_query(Text(startswith="things_list"), any_state)
# async def next_page(call: types.CallbackQuery, state: FSMContext):
#     data = call.data.split("|")
#     number_page = int(data[2])
#     next_or_back = data[1]
#     category = data[3]
#     if next_or_back == "page_next":
#         number_page += 1
#     else:
#         if number_page != 0:
#             number_page -= 1
#     keyboard = Paginator(Things(category).user_things.get(category), category)
#     keyboard = await keyboard.generate_things_list_keyboard(number_page)
#     await call.message.edit_text(f"Объявления из категории {category}:")
#     await call.message.edit_reply_markup(reply_markup=keyboard.as_markup())


# @router.message(Text(text="Позвать друга🔶", ignore_case=True))
# async def visit_friend(message: types.Message, state: FSMContext):
#     await message.reply("Отлично, отправь мне ФИО своего гостя, если их несколько, укажи через запятую",
#                         reply_markup=cancel_keyboard)
#     await state.set_state(InputMessage.calling_guests)
#
#
# @router.message(F.text, InputMessage.calling_guests)
# async def visit_friend(message: types.Message, state: FSMContext):
#     await state.set_state(InputMessage.time_guests)
#     await state.update_data(initiels=message.text)
#     await message.reply(f"Отлично, отправь мне приблизительное время к которому он(и) подойдут (с 9 до 20 часов) "
#                         f"в формате ЧЧ:MM, например, <b>15:20</b>",
#                         reply_markup=cancel_keyboard)
#
#
# @router.message(F.text, InputMessage.time_guests)
# async def visit_friend(message: types.Message, state: FSMContext):
#     # print(await state.get_data())
#     try:
#         time_visit = datetime.time(int(message.text[:2]), int(message.text[3:]))
#         # print(str(time_visit), type(time_visit))
#         if datetime.time(9, 0) < time_visit < datetime.time(20, 0):
#             data = await state.get_data()
#             data["time"] = time_visit
#             # await state.update_data(data)
#             await message.reply("Отлично, отправь мне свой личный код!", reply_markup=restore_keyboard)
#             await state.set_state(InputMessage.code_confirm)
#             await state.update_data(data)
#         else:
#             await message.reply("В это время нельзя приводить гостей, попробуй уще раз!",
#                                 reply_markup=cancel_keyboard)
#     except:
#         await message.reply("Ты ввел неправильный формат времени, попробуй еще раз!",
#                             reply_markup=cancel_keyboard)
#
#
# @router.message(Text(text="Забыл код", ignore_case=True), InputMessage.code_confirm)
# async def visit_friend(message: types.Message, state: FSMContext):
#     await message.reply("Для подтверждения напиши свой email от ЛКС в виде login@edu.mirea.ru",
#                         reply_markup=cancel_keyboard)
#     data = await state.get_data()
#     await state.set_state(InputMessage.enter_email)
#     await state.update_data(data)
#
#
# @router.message(F.text, InputMessage.enter_email)
# async def visit_friend(message: types.Message, state: FSMContext):
#     if message.text == await Users(str(message.from_user.id)).get_email():
#         await message.reply("Отлично, напиши свой пороль от ЛКС",
#                             reply_markup=cancel_keyboard)
#         data = await state.get_data()
#         await state.set_state(InputMessage.enter_password)
#         await state.update_data(data)
#     else:
#         await message.reply("Ты ввел неверный email, попробуй повторить!", reply_markup=cancel_keyboard)
#
#
# @router.message(F.text, InputMessage.enter_password)
# async def visit_friend(message: types.Message, state: FSMContext):
#     if message.text == await Users(str(message.from_user.id)).get_password():
#         await message.reply("Отлично, напиши свой новый пин-код любой длины (не менее 4 цифр)!",
#                             reply_markup=cancel_keyboard)
#         data = await state.get_data()
#         await state.set_state(InputMessage.enter_code)
#         await state.update_data(data)
#     else:
#         await message.reply("Ты ввел неверный пороль, попробуй повторить!", reply_markup=cancel_keyboard)
#
#
# @router.message(F.text, InputMessage.enter_code)
# async def visit_friend(message: types.Message, state: FSMContext):
#     if message.text.isdigit():
#         await Users(str(message.from_user.id)).add_secret_code(int(message.text))
#         await message.answer("Отлично твой код обновлен! Введи его для сохранения заявки",
#                             reply_markup=cancel_keyboard)
#         data = await state.get_data()
#         await state.set_state(InputMessage.code_confirm)
#         await state.update_data(data)
#         await message.delete()
#     else:
#         await message.reply("Твой код должен состоять только из цифр, попробуй еще раз!",
#                             reply_markup=cancel_keyboard)
#
#
# @router.message(F.text, InputMessage.code_confirm)
# async def visit_friend(message: types.Message, state: FSMContext, bot: Bot):
#     if message.text == str(await Users(str(message.from_user.id)).get_code()):
#         await message.delete()
#         data = await state.get_data()
#         users_api = Users(str(message.from_user.id))
#         await bot.send_message(chat_id=security_ids[0],
#                                text=f"Вам пришло оповещение! {await users_api.get_initials()}"
#                                     f" пригласил {data.get('initiels')}"
#                                     f" к себе в гости! Примерное время прибытия: {str(data.get('time'))[:-3]}")
#         await message.answer(f"Отлично, ваша заявка отправлена! "
#                              f"Вы пригласили {data.get('initiels')} к себе в гости!"
#                              f" Примерное время прибытия: {str(data.get('time'))[:-3]}", reply_markup=profile_keyboard)
#         await state.clear()
#     else:
#         await message.reply("Ты ввел неправильный код, попробуй еще раз!",
#                             reply_markup=cancel_keyboard)
#
#
# @router.callback_query(Text(text="Отмена❌"), any_state)
# async def answer_to_user(call: types.CallbackQuery, state: FSMContext):
#     await call.message.delete()
#     await state.clear()
#     await call.message.answer("Выбери свои дальнейшие действия", reply_markup=profile_keyboard)
#
#
# @end_router.message(any_state)
# async def starting(message: types.Message):
#     await message.answer('👋Я вас не понимать! Выберите свои дальнейшие действия!',
#                          reply_markup=start_keyboard)
