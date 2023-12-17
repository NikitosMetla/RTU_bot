from aiogram import types, F
from aiogram import Router
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import any_state
from aiogram.types import InlineKeyboardButton

from data.keyboards import profile_keyboard, categories_keyboard, buy_or_sell_keyboard
from db.user_things import Things
from utils.data_of_thing import CreateThing

from data.settings import InputMessage, categories


selling_router = Router()


@selling_router.callback_query(Text(contains="Отмена❌|"), any_state)
async def cancel_thing(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.clear()
    data = call.data.split("|")[1:]
    thing = Things(category=data[0], user_id=data[1], thing_id=data[2])
    await thing.delete_thing()
    await call.message.answer("Выбери свои дальнейшие действия", reply_markup=profile_keyboard)


@selling_router.callback_query(Text(text="back_to_startpage"), any_state)
@selling_router.message(Text(text="Барахолка💵", ignore_case=True), any_state)
async def go_to_shop(message: types.Message | types.CallbackQuery, state: FSMContext):
    if type(message) == types.Message:
        await message.answer("Отлично, выбери свои дальнейшие действия!",
                             reply_markup=buy_or_sell_keyboard.as_markup())
        return
    await message.message.edit_text("Отлично, выбери свои дальнейшие действия!",
                                    reply_markup=buy_or_sell_keyboard.as_markup())


@selling_router.callback_query(Text(text="sell_thing", ignore_case=True), any_state)
async def selling(message: types.CallbackQuery, state: FSMContext):
    await state.set_state(InputMessage.enter_category)
    await message.message.edit_text("Выберите категорию своего товара!", reply_markup=categories_keyboard.as_markup())


@selling_router.callback_query(lambda call: call.data in categories and call.data != "Отмена❌",
                               InputMessage.enter_category)
async def choise_category(call: types.CallbackQuery, state: FSMContext):
    thing = Things(category=call.data)
    await thing.add_thing(user_id=call.from_user.id)
    thing_id = thing.thing_id
    keyboard = CreateThing(category=call.data, user_id=call.from_user.id, thing_id=thing_id)
    keyboard = await keyboard.data_thing_keyboard()
    keyboard.row(InlineKeyboardButton(text="🔙Назад на начальную страницу",
                                      callback_data="back_to_startpage"))
    keyboard.row(InlineKeyboardButton(text="Удалить объявление❌", callback_data=f"Отмена❌|{thing.category}|"
                                                                    f"{thing.user_id}|{thing.thing_id}"))
    await call.message.edit_text(f"Твое объявление:\n"
                                 f"Категория: {thing.category}\n"
                                 f"Название вещи: {await thing.get_name()}\n"
                                 f"Цена: {await thing.get_price()}\n"
                                 f"Состояние: {await thing.get_state_thing()}\n"
                                 f"Описание: {await thing.get_description()}\n"
                                 f"Фотографии:", reply_markup=keyboard.as_markup())
    await state.clear()


@selling_router.callback_query(Text(startswith="edit_category|"), any_state)
async def new_name(call: types.CallbackQuery, state: FSMContext):
    data = call.data.split("|")[1:]
    await state.set_state(InputMessage.edit_category)
    await state.update_data(category=data[0], user_id=data[1], thing_id=data[2])
    await call.message.edit_text("Выберите категорию своего товара!", reply_markup=categories_keyboard.as_markup())


@selling_router.callback_query(lambda call: call.data in categories and call.data != "Отмена❌",
                               InputMessage.edit_category)
async def edit_category(call: types.CallbackQuery, state: FSMContext):
    delete_data = await state.get_data()
    old_thing = Things(category=delete_data.get("category"), user_id=delete_data.get("user_id"),
                             thing_id=delete_data.get("thing_id"))
    my_thing = await old_thing.get_thing_data()
    await old_thing.delete_thing()
    thing = Things(category=call.data)
    await thing.add_thing(user_id=call.from_user.id)
    thing_id = thing.thing_id
    my_thing["thing_id"] = thing_id
    await thing.edit_thing_data(my_thing)
    keyboard = CreateThing(category=call.data, user_id=call.from_user.id, thing_id=thing_id)
    keyboard = await keyboard.data_thing_keyboard()
    keyboard.row(InlineKeyboardButton(text="🔙Назад на начальную страницу",
                                      callback_data="back_to_startpage"))
    keyboard.row(InlineKeyboardButton(text="Удалить объявление❌", callback_data=f"Отмена❌|{thing.category}|"
                                                                    f"{thing.user_id}|{thing.thing_id}"))
    await call.message.edit_text(f"Твое объявление:\n"
                                 f"Категория: {thing.category}\n"
                                 f"Название вещи: {await thing.get_name()}\n"
                                 f"Цена: {await thing.get_price()}\n"
                                 f"Состояние: {await thing.get_state_thing()}\n"
                                 f"Описание: {await thing.get_description()}\n"
                                 f"Фотографии:", reply_markup=keyboard.as_markup())
    await state.clear()


@selling_router.callback_query(Text(contains="name"), any_state)
async def new_name(call: types.CallbackQuery, state: FSMContext):
    data = call.data.split("|")
    data = "|".join(data[1:])
    await state.set_state(InputMessage.enter_name)
    await state.update_data(thing=data)
    await call.message.edit_text("Введите название вещи")


@selling_router.message(F.text, InputMessage.enter_name)
async def enter_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    data = data.get("thing").split("|")
    category = data[0]
    user_id = data[1]
    thing_id = data[2]
    thing = Things(category=category, user_id=user_id, thing_id=thing_id)
    keyboard = CreateThing(category=category, user_id=message.from_user.id, thing_id=thing_id)
    keyboard = await keyboard.data_thing_keyboard()
    keyboard.row(InlineKeyboardButton(text="🔙Назад на начальную страницу",
                                      callback_data="back_to_startpage"))
    keyboard.row(InlineKeyboardButton(text="Удалить объявление❌", callback_data=f"Отмена❌|{thing.category}|"
                                                                   f"{thing.user_id}|{thing.thing_id}"))
    await thing.edit_name(message.text)
    await message.reply(text=f"Твое объявление:\n"
                             f"Категория: {category}\n"
                             f"Название вещи: {await thing.get_name()}\n"
                             f"Цена: {await thing.get_price()}\n"
                             f"Состояние: {await thing.get_state_thing()}\n"
                             f"Описание: {await thing.get_description()}\n"
                             f"Фотографии:", reply_markup=keyboard.as_markup())


@selling_router.callback_query(Text(contains="price"), any_state)
async def new_price(call: types.CallbackQuery, state: FSMContext):
    data = call.data.split("|")
    data = "|".join(data[1:])
    await state.set_state(InputMessage.enter_price)
    await state.update_data(thing=data)
    await call.message.edit_text("Введите цену товара")


@selling_router.message(F.text, InputMessage.enter_price)
async def enter_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    data = data.get("thing").split("|")
    category = data[0]
    user_id = data[1]
    thing_id = data[2]
    thing = Things(category=category, user_id=user_id, thing_id=thing_id)
    keyboard = CreateThing(category=category, user_id=message.from_user.id, thing_id=thing_id)
    keyboard = await keyboard.data_thing_keyboard()
    keyboard.row(InlineKeyboardButton(text="🔙Назад на начальную страницу",
                                      callback_data="back_to_startpage"))
    keyboard.row(InlineKeyboardButton(text="Удалить объявление❌", callback_data=f"Отмена❌|{thing.category}|"
                                                                   f"{thing.user_id}|{thing.thing_id}"))
    await thing.edit_price(message.text)
    await message.reply(text=f"Твое объявление:\n"
                             f"Категория: {category}\n"
                             f"Название вещи: {await thing.get_name()}\n"
                             f"Цена: {await thing.get_price()}\n"
                             f"Состояние: {await thing.get_state_thing()}\n"
                             f"Описание: {await thing.get_description()}\n"
                             f"Фотографии:", reply_markup=keyboard.as_markup())


@selling_router.callback_query(Text(contains="state"), any_state)
async def new_state(call: types.CallbackQuery, state: FSMContext):
    data = call.data.split("|")
    data = "|".join(data[1:])
    await state.set_state(InputMessage.enter_state)
    await state.update_data(thing=data)
    await call.message.edit_text("Введите состояние вещи")


@selling_router.message(F.text, InputMessage.enter_state)
async def enter_state(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    data = data.get("thing").split("|")
    category = data[0]
    user_id = data[1]
    thing_id = data[2]
    thing = Things(category=category, user_id=user_id, thing_id=thing_id)
    keyboard = CreateThing(category=category, user_id=message.from_user.id, thing_id=thing_id)
    keyboard = await keyboard.data_thing_keyboard()
    keyboard.row(InlineKeyboardButton(text="🔙Назад на начальную страницу",
                                      callback_data="back_to_startpage"))
    keyboard.row(InlineKeyboardButton(text="Удалить объявление❌", callback_data=f"Отмена❌|{thing.category}|"
                                                                   f"{thing.user_id}|{thing.thing_id}"))
    await thing.edit_state_thing(message.text)
    await message.reply(text=f"Твое объявление:\n"
                             f"Категория: {category}\n"
                             f"Название вещи: {await thing.get_name()}\n"
                             f"Цена: {await thing.get_price()}\n"
                             f"Состояние: {await thing.get_state_thing()}\n"
                             f"Описание: {await thing.get_description()}\n"
                             f"Фотографии:", reply_markup=keyboard.as_markup())


@selling_router.callback_query(Text(contains="description"), any_state)
async def new_description(call: types.CallbackQuery, state: FSMContext):
    data = call.data.split("|")
    data = "|".join(data[1:])
    await state.set_state(InputMessage.enter_description)
    await state.update_data(thing=data)
    await call.message.edit_text("Введите описание вещи")


@selling_router.message(F.text, InputMessage.enter_description)
async def enter_description(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    data = data.get("thing").split("|")
    category = data[0]
    user_id = data[1]
    thing_id = data[2]
    thing = Things(category=category, user_id=user_id, thing_id=thing_id)
    keyboard = CreateThing(category=category, user_id=message.from_user.id, thing_id=thing_id)
    keyboard = await keyboard.data_thing_keyboard()
    keyboard.row(InlineKeyboardButton(text="🔙Назад на начальную страницу",
                                      callback_data="back_to_startpage"))
    keyboard.row(InlineKeyboardButton(text="Удалить объявление❌", callback_data=f"Отмена❌|{thing.category}|"
                                                                   f"{thing.user_id}|{thing.thing_id}"))
    await thing.edit_description(message.text)
    await message.reply(text=f"Твое объявление:\n"
                             f"Категория: {category}\n"
                             f"Название вещи: {await thing.get_name()}\n"
                             f"Цена: {await thing.get_price()}\n"
                             f"Состояние: {await thing.get_state_thing()}\n"
                             f"Описание: {await thing.get_description()}\n"
                             f"Фотографии:", reply_markup=keyboard.as_markup())