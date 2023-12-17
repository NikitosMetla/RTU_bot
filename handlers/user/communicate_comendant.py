import asyncio

from aiogram import Bot, types, Router
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.keyboards import profile_keyboard, cancel_keyboard
from db.all_dormitories import Dormitory
from db.students_requests_for_admins import Request
from datetime import timedelta

from db.users import Users

from data.settings import InputMessage


com_comendant_router = Router()


@com_comendant_router.message(Text(text="Связь с комендантом💬", ignore_case=True))
async def com_commendant(message: types.Message, state: FSMContext):
    await message.reply("Отлично, отправь свой вопрос или просьбу! Постарайся все описать подробнее,"
                        " твои инициалы и место проживания добавится автоматически к тексту твоей заявки."
                        " По необходимости можете"
                        " прикрепить одну фотографию",
                        reply_markup=cancel_keyboard)
    await state.set_state(InputMessage.message_to_comendant)


@com_comendant_router.message(InputMessage.message_to_comendant)
async def message_to_commendant(message: types.Message, state: FSMContext, bot: Bot):
    users_api = Users(message.from_user.id)
    floor = await users_api.get_floor()
    room = await users_api.get_room()
    try:
        if (floor is None) or (room is None):
            await message.reply("Ваше сообщение <b>НЕ ОТПРАВЛЕНО</b> комендантам!"
                                " Убедись, что ты ввел все свои данные о проживании!", reply_markup=profile_keyboard)
            await state.clear()
            return
        obchaga = await users_api.get_number_of_obchaga()
        request = Request(obchaga=obchaga, user_id=message.from_user.id, floor=floor, room=room)
        keyboard = InlineKeyboardBuilder()
        keyboard.row(types.InlineKeyboardButton(text="Принять в обработку", callback_data=f"accept_processing|"
                                                                                          f"{obchaga}|"
                                                                                          f"{request.request_id}"))
        admins_obchaga = await Dormitory(obchaga=obchaga).get_obchaga_admins()
        if message.photo is None:
            text_message = (f"Вам пришла заявка №{request.request_id} от {await users_api.get_initials()}"
                            f" с <b>{floor}</b> этажа"
                            f" из комнаты <b>{room}</b>:\n{message.text}\n"
                            f"Дата и время отправки: <b>{str(message.date + timedelta(hours=3))[:-6]}</b>")
            task_list = [asyncio.create_task(bot.send_message(chat_id=user,
                                                              text=text_message,
                                                              reply_markup=keyboard.as_markup()))
                         for user in admins_obchaga.keys()]
            messages_for_admins = await asyncio.gather(*task_list)
            messages_ids = {message_admin.chat.id: message_admin.message_id for message_admin in messages_for_admins}
            await request.add_request(text_request=text_message, messages_for_admins=messages_ids,
                                      date=str(message.date + timedelta(hours=3)))
        else:
            if message.caption is None:
                caption = ""
            else:
                caption = message.caption
            text_message = (f"Вам пришла заявка №{request.request_id} от {await users_api.get_initials()}"
                            f" с {floor} этажа"
                            f" из комнаты {room}:\n{caption}\n"
                            f"<i>Дата и время отправки:</i> <b>{str(message.date + timedelta(hours=3))[:-6]}</b>")
            task_list = [asyncio.create_task(bot.send_photo(chat_id=user, photo=message.photo[-1].file_id,
                                                            caption=text_message, reply_markup=keyboard.as_markup()))
                         for user in admins_obchaga.keys()]
            messages_for_admins = await asyncio.gather(*task_list)
            messages_ids = {message_admin.chat.id: message_admin.message_id for message_admin in messages_for_admins}
            await request.add_request(text_request=text_message,
                                      messages_for_admins=messages_ids,
                                      photo_id=message.photo[-1].file_id,
                                      date=str(message.date + timedelta(hours=3)))
        await message.reply(f"Ваше сообщение отправлено комендантам! Номер заявки:"
                            f" {request.request_id}",
                            reply_markup=profile_keyboard)
        await state.clear()
    except:
        await message.reply("Ваше сообщение <b>НЕ ОТПРАВЛЕНО</b> комендантам!"
                            " Убедись, что ты ввел все свои данные о проживании!", reply_markup=profile_keyboard)
        await state.clear()