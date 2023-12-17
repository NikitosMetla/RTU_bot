from aiogram import Bot, types, F, Router
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import any_state
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.keyboards import profile_keyboard
from db.user_things import Things
from utils.is_username import is_username
from utils.paginator import Paginator
from utils.data_of_thing import CreateThing

from data.settings import (InputMessage, moderators)


my_thigs_router = Router()


@my_thigs_router.callback_query(Text(text="my_things"), any_state)
async def my_things(message: types.CallbackQuery, state: FSMContext):
    keyboard = await Paginator().generate_my_things_keyboard(message.from_user.id)
    await message.message.edit_text("Мои объявления из всех категорий:", reply_markup=keyboard.as_markup())


@my_thigs_router.callback_query(Text(text="back_to_things"), any_state)
async def my_things(call: types.CallbackQuery, state: FSMContext):
    keyboard = await Paginator().generate_my_things_keyboard(call.from_user.id)
    await call.message.edit_text("Мои объявления из всех категорий:", reply_markup=keyboard.as_markup())


@my_thigs_router.callback_query(Text(contains="my_thing|"), any_state)
async def getting_thing(call: types.CallbackQuery, state: FSMContext):
    data = call.data.split("|")
    user_id = data[2]
    thing_id = data[1]
    category = data[3]
    thing = Things(category=category, user_id=user_id, thing_id=thing_id)
    keyboard = await CreateThing(category=category, user_id=user_id, thing_id=thing_id).edit_thing_keyboard()
    if not (await thing.get_verified()):
        keyboard.row(InlineKeyboardButton(text="Отправить на модерацию", callback_data=f"Отправить|{category}|"
                                                                                       f"{user_id}|{thing_id}"))
    await call.message.edit_text(f"Категория: {category}"
                                 f"Название: {await thing.get_name()}\n"
                                 f"Состояние: {await thing.get_state_thing()}\n"
                                 f"Цена: {await thing.get_price()}\n"
                                 f"Описание: {await thing.get_description()}",
                                 reply_markup=keyboard.as_markup())


@my_thigs_router.callback_query(Text(startswith="my_things"), any_state)
async def next_page(call: types.CallbackQuery, state: FSMContext):
    data = call.data.split("|")
    number_page = int(data[2])
    next_or_back = data[1]
    if next_or_back == "page_next":
        number_page += 1
    else:
        if number_page != 0:
            number_page -= 1
    keyboard = await Paginator().generate_my_things_keyboard(user_id=call.from_user.id, page=number_page)
    await call.message.edit_text("Мои объявления из всех категорий:")
    await call.message.edit_reply_markup(reply_markup=keyboard.as_markup())


@my_thigs_router.callback_query(Text(contains="edit_thing"), any_state)
@is_username
async def editing_thing(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    data = call.data.split("|")[1:]
    category, user_id, thing_id = data[0], data[1], data[2]
    keyboard = CreateThing(category=category, user_id=user_id, thing_id=thing_id)
    keyboard = await keyboard.data_thing_keyboard()
    thing = Things(category=category, user_id=user_id, thing_id=thing_id)
    keyboard.row(InlineKeyboardButton(text="🔙Назад к моим объявлениям", callback_data="back_to_things"))
    await thing.edit_verified(False)
    await call.message.edit_text(f"Твое объявление:\n"
                                 f"Категория: {category}\n"
                                 f"Название вещи: {await thing.get_name()}\n"
                                 f"Цена: {await thing.get_price()}\n"
                                 f"Состояние: {await thing.get_state_thing()}\n"
                                 f"Описание: {await thing.get_description()}\n"
                                 f"Фотографии:",
                                 reply_markup=keyboard.as_markup())


@my_thigs_router.callback_query(Text(contains="delete_thing|"), any_state)
async def deleting_thing(call: types.CallbackQuery, state: FSMContext):
    data = call.data.split("|")[1:]
    confirm_action = InlineKeyboardBuilder()
    confirm_action.row(InlineKeyboardButton(text=f"Да", callback_data=f"DELETE|{'|'.join(data)}"))
    confirm_action.row(InlineKeyboardButton(text=f"Нет", callback_data=f"NOT_DELETE|{'|'.join(data)}"))
    await call.message.edit_text("Вы уверены, что хотите удалить объявление?", reply_markup=confirm_action.as_markup())


@my_thigs_router.callback_query(Text(startswith="DELETE|"), any_state)
async def delete_forever(call: types.CallbackQuery, state: FSMContext):
    data = call.data.split("|")[1:]
    thing = await Things(category=data[0], user_id=data[1], thing_id=data[2]).delete_thing()
    await call.message.edit_text("Ваше объявление было удалено!")
    keyboard = await Paginator().generate_my_things_keyboard(call.from_user.id)
    await call.message.answer("Выши объявления:", reply_markup=keyboard.as_markup())


@my_thigs_router.callback_query(Text(contains="NOT_DELETE|"), any_state)
async def not_deleting(call: types.CallbackQuery, state: FSMContext):
    keyboard = await Paginator().generate_my_things_keyboard(call.from_user.id)
    await call.message.edit_text("Ваши объявления:", reply_markup=keyboard.as_markup())


@my_thigs_router.callback_query(Text(contains="Отправить|"), any_state)
async def give_to_moder(call: types.CallbackQuery, state: FSMContext):
    data = call.data.split("|")[1:]
    thing = Things(category=data[0], user_id=data[1], thing_id=data[2])
    confirm_action = InlineKeyboardBuilder()
    confirm_action.row(InlineKeyboardButton(text=f"Да", callback_data=f"MODER|{'|'.join(data)}"))
    confirm_action.row(InlineKeyboardButton(text=f"Нет", callback_data=f"NOT_MODER|{'|'.join(data)}"))
    await call.message.edit_text("Вы уверены, что хотите выложить объявление?", reply_markup=confirm_action.as_markup())


@my_thigs_router.callback_query(Text(startswith="MODER|"), any_state)
async def moderation(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    data = call.data.split("|")[1:]
    thing = Things(category=data[0], user_id=data[1], thing_id=data[2])
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text=f"Одобрить", callback_data=f"APPROVE|{'|'.join(data)}"))
    keyboard.row(InlineKeyboardButton(text=f"Отменить одобрение", callback_data=f"NOT_APPROVE|{'|'.join(data)}"))
    await bot.send_message(moderators[0], f"Вам пришло новое объявление!\nНазвание: {await thing.get_name()}\n"
                                               f"Состояние: {await thing.get_state_thing()}\n"
                                               f"Цена: {await thing.get_price()}\n"
                                               f"Описание: {await thing.get_description()}",
                           reply_markup=keyboard.as_markup())
    await call.message.delete()
    await call.message.answer("Ваше объявление отправлено на модерацию!", reply_markup=profile_keyboard)


@my_thigs_router.callback_query(Text(startswith="APPROVE|"), any_state)
async def moder_approve(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    data = call.data.split("|")[1:]
    thing = Things(category=data[0], user_id=data[1], thing_id=data[2])
    await thing.edit_verified(True)
    await call.message.edit_text("Отлично, вы одобрили заявку!")
    await bot.send_message(chat_id=thing.user_id, text=f"Ваше объявление <b>{await thing.get_name()}</b>"
                                                       f" одобрено модератором и доступно к просмотру!")


@my_thigs_router.callback_query(Text(contains="NOT_MODER|"), any_state)
async def not_moderation(call: types.CallbackQuery, state: FSMContext):
    keyboard = await Paginator().generate_my_things_keyboard(call.from_user.id)
    await call.message.edit_text("Выши объявления:", reply_markup=keyboard.as_markup())


@my_thigs_router.callback_query(Text(startswith="NOT_APPROVE|"), any_state)
async def moder_not_approve(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(InputMessage.comment_to_thing)
    data = call.data.split("|")[1:]
    await state.update_data(new_data=call.data)
    thing = Things(category=data[0], user_id=data[1], thing_id=data[2])
    await thing.edit_verified(False)
    await call.message.edit_text("Напишите комментарий, почему вы не одобрили заявку!")


@my_thigs_router.message(F.text, InputMessage.comment_to_thing)
async def comment_to_not_approve(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    data = data.get("new_data").split("|")[1:]
    user_id = data[1]
    thing = Things(category=data[0], user_id=data[1], thing_id=data[2])
    text = (f"Ваша заявка на публикацию вещи <b>{await thing.get_name()}</b> не одобрена.\n"
            f"Комментарий модератора:\n<b>{message.text}</b>")
    await bot.send_message(chat_id=user_id, text=text)
    await state.clear()