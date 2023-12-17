from aiogram import types, Router
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import any_state
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.keyboards import profile_keyboard, categories_keyboard
from db.user_things import Things
from utils.paginator import Paginator

from data.settings import categories


list_things_router = Router()


@list_things_router.callback_query(Text(contains="get_categories"), any_state)
@list_things_router.callback_query(Text(text="view_things", ignore_case=True), any_state)
async def viewing_things(message: types.Message or types.CallbackQuery, state: FSMContext):
    if message.data == "view_things":
        await message.message.edit_text("Отлично, выбери категорию для просмотра!",
                                        reply_markup=categories_keyboard.as_markup())
        return
    await message.message.edit_text("Отлично, выбери категорию для просмотра!",
                                    reply_markup=categories_keyboard.as_markup())


@list_things_router.callback_query(Text(text="Отмена❌"), any_state)
async def canceling(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.clear()
    await call.message.answer("Выбери свои дальнейшие действия", reply_markup=profile_keyboard)


@list_things_router.callback_query(lambda call: call.data in categories and call.data != "Отмена❌", any_state)
async def choise_category(call: types.CallbackQuery, state: FSMContext):
    things = Paginator(Things(call.data).user_things.get(call.data), call.data)
    keyboard = await things.generate_things_list_keyboard()
    await call.message.edit_text(f"Объявления из категории {call.data}:")
    await call.message.edit_reply_markup(reply_markup=keyboard.as_markup())


@list_things_router.callback_query(Text(contains="get_thing"), any_state)
async def getting_thing(call: types.CallbackQuery, state: FSMContext):
    data = call.data.split("|")
    user_id = data[2]
    thing_id = data[1]
    category = data[3]
    thing = Things(category=category, user_id=user_id, thing_id=thing_id)
    back_to_categories = InlineKeyboardBuilder()
    back_to_categories.row(InlineKeyboardButton(text="Связаться с продавцом", callback_data="communicate_salesman|"
                                                                                            + "|".join(data[1:])))
    back_to_categories.row(InlineKeyboardButton(text="🔙Назад к объявлениям", callback_data=category))
    await call.message.edit_text(f"Название: {await thing.get_name()}\n"
                                 f"Состояние: {await thing.get_state_thing()}\n"
                                 f"Цена: {await thing.get_price()}\n"
                                 f"Описание: {await thing.get_description()}",
                                 reply_markup=back_to_categories.as_markup())


@list_things_router.callback_query(Text(startswith="communicate_salesman"), any_state)
async def com_salesman(call: types.CallbackQuery, state: FSMContext):
    data = call.data.split("|")
    user_id = data[2]
    thing_id = data[1]
    category = data[3]
    thing = Things(category=category, user_id=user_id, thing_id=thing_id)
    back_to_categories = InlineKeyboardBuilder()
    back_to_categories.row(InlineKeyboardButton(text="🔙Назад к объявлениям", callback_data=category))
    await call.message.edit_text(f"Название: {await thing.get_name()}\n"
                                 f"Состояние: {await thing.get_state_thing()}\n"
                                 f"Цена: {await thing.get_price()}\n"
                                 f"Описание: {await thing.get_description()}\n"
                                 f"Ссылка на продавца {call.from_user.url}",
                                 reply_markup=back_to_categories.as_markup())


@list_things_router.callback_query(Text(startswith="things_list"), any_state)
async def next_page(call: types.CallbackQuery, state: FSMContext):
    data = call.data.split("|")
    number_page = int(data[2])
    next_or_back = data[1]
    category = data[3]
    if next_or_back == "page_next":
        number_page += 1
    else:
        if number_page != 0:
            number_page -= 1
    keyboard = Paginator(Things(category).user_things.get(category), category)
    keyboard = await keyboard.generate_things_list_keyboard(number_page)
    await call.message.edit_text(f"Объявления из категории {category}:")
    await call.message.edit_reply_markup(reply_markup=keyboard.as_markup())