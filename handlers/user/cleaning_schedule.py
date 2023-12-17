import asyncio

from aiogram import types, Router, Bot
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import any_state
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.keyboards import profile_keyboard, check_in_cleaning, back_to_graphic
from data.settings import comendant_ids
from db.all_dormitories import Dormitory
from db.users import Users

cleaning_router = Router()


@cleaning_router.message(Text(text="График уборкиℹ️", ignore_case=True))
async def cleaning(message: types.Message, state: FSMContext):
    await message.answer("Выберите свои дальнейшие действия!", reply_markup=check_in_cleaning.as_markup())


@cleaning_router.callback_query(Text(contains="Посмотреть свой график📅"), any_state)
async def view_graphic(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(f"<b>Вы выбрали просмотр своего графика:</b>\n"
                                 f"<i>День недели:</i> Четверг\n<i>Время</i>: 14:00-16:00\n"
                                 f"<i>Место проведения:</i> Общежитие №1, 2 этаж"
                                 f"\n<b><i>Если вы хотите изменить график,"
                                 f" обратитесь к коменданту через бота или очно</i></b>",
                                 reply_markup=back_to_graphic.as_markup())


@cleaning_router.callback_query(Text(contains="Начать уборку▶️"), any_state)
async def confirm_start_cleaning(call: types.CallbackQuery, state: FSMContext):
    confirm_start_cleaning_keyboard = InlineKeyboardBuilder()
    confirm_start_cleaning_keyboard.row(InlineKeyboardButton(text="Да", callback_data="confirm_start"))
    confirm_start_cleaning_keyboard.row(InlineKeyboardButton(text="Нет", callback_data="not_confirm_start"))
    await call.message.edit_text(text="Вы уверены, что хотите начать уборку?",
                                 reply_markup=confirm_start_cleaning_keyboard.as_markup())


@cleaning_router.callback_query(Text(contains="not_confirm_start"), any_state)
async def start_work(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Выберите свои дальнейшие действия!", reply_markup=check_in_cleaning.as_markup())


@cleaning_router.callback_query(Text(contains="confirm_start"), any_state)
async def start_work(call: types.CallbackQuery, bot: Bot):
    try:
        keyboard = InlineKeyboardBuilder()
        keyboard.row(InlineKeyboardButton(text="Завершить уборку☑️", callback_data="end_cleaning"))
        users_api = Users(call.from_user.id)
        headman_id = await Dormitory(obchaga=await users_api.get_number_of_obchaga(),
                                     floor=await users_api.get_floor()).get_headman()
        if len(headman_id) > 0:
            headman_id = list(headman_id.keys())
            task_list = [asyncio.create_task(bot.send_message(chat_id=headman,
                                                              text=f"Комната {await users_api.get_room()}"
                                                                   f" начала уборку!")) for headman in headman_id]
            await asyncio.gather(*task_list)
            await call.message.edit_text(f"Вы начали уборку, старостам этажа пришло уведомление об этом.\n"
                                         f"Нажмите кнопку, когда закончите убираться!",
                                         reply_markup=keyboard.as_markup())
        else:
            await call.message.edit_text(f"Уведомление не отправлено старостам этажа, вы либо ввели неверные данные о"
                                         f" своем месте проживания, либо на данном этаже нет старосты",
                                         reply_markup=back_to_graphic.as_markup())
    except:
        await call.message.edit_text(f"Уведомление не отправлено старостам этажа, вы ввели неверные данные о"
                                     f" своем месте проживания или не ввели их вовсе!",
                                     reply_markup=back_to_graphic.as_markup())


@cleaning_router.callback_query(Text(text="end_cleaning"), any_state)
async def ending_cleaning(call: types.CallbackQuery, state: FSMContext):
    confirm_cleaning_keyboard = InlineKeyboardBuilder()
    confirm_cleaning_keyboard.row(InlineKeyboardButton(text="Да", callback_data="confirm_cleaning"))
    confirm_cleaning_keyboard.row(InlineKeyboardButton(text="Нет", callback_data="not_confirm_cleaning"))
    await call.message.edit_text("Вы уверены, что хотите закончить уборку?",
                                 reply_markup=confirm_cleaning_keyboard.as_markup())


@cleaning_router.callback_query(Text(text="confirm_cleaning"), any_state)
async def confirm_cleaning(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    users_api = Users(call.from_user.id)
    headman_id = await Dormitory(obchaga=await users_api.get_number_of_obchaga(),
                                 floor=await users_api.get_floor()).get_headman()
    headman_id = list(headman_id.keys())
    try:
        for headman in headman_id:
            await bot.send_message(
                chat_id=headman,
                text=f"Комната {await users_api.get_room()} завершила уборку! Требуется проверить!")
        await call.message.edit_text(f"Отлично, старостам этажа пришло уведомление о завершении уборки!"
                                     f" В ближайшее время он подойдет на место и проведет проверку",
                                     reply_markup=back_to_graphic.as_markup())
    except:
        await call.message.edit_text(f"Уведомление не отправлено старосте этажа, проверьте,"
                                     f" правильно ли вы ввели данные о вашем месте проживания",
                                     reply_markup=back_to_graphic.as_markup())


@cleaning_router.callback_query(Text(text="not_confirm_cleaning"), any_state)
async def confirm_cleaning(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    await start_work(call, FSMContext, Bot)


@cleaning_router.callback_query(Text(text="graphic_cleaning"), any_state)
async def confirm_cleaning(call: types.CallbackQuery, state: FSMContext):
    await cleaning(call.message, FSMContext)
    await call.message.delete()
