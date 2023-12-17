from aiogram import Bot, types, Router
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import any_state
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.keyboards import profile_keyboard, cancel_keyboard

from data.settings import (InputMessage, develop_ids)


com_develop_router = Router()


@com_develop_router.message(Text(text="Связь с разработчиками💬", ignore_case=True))
async def com_developer(message: types.Message, state: FSMContext):
    await state.set_state(InputMessage.message_to_developer)
    await message.reply("Напишите какой вопрос или предложение, который вы хотите передать разработчикам."
                        " При необходимости прикрепите фотографию",
                        reply_markup=cancel_keyboard)


@com_develop_router.message(Text(text="Отмена❌", ignore_case=True), any_state)
async def canceling(message: types.Message, state: FSMContext):
    await state.clear()
    await message.reply("Выбери свои дальнейшие действия", reply_markup=profile_keyboard)


@com_develop_router.message(InputMessage.message_to_developer)
async def message_to_developer(message: types.Message, state: FSMContext, bot: Bot):
    keyboard_for_develop = InlineKeyboardBuilder()
    keyboard_for_develop.row(InlineKeyboardButton(text=f"Ответить пользователю?",
                                                  callback_data=f"Ответить пользователю {message.from_user.id}"))
    keyboard_for_develop.row(InlineKeyboardButton(text="Игнорировать", callback_data="No"))
    if message.photo is not None:
        text_message = "<b>Сообщение от пользователя: </b>" + message.caption + "\n" + \
                       f"user_id: {message.from_user.id}" + "\nХотите ответить пользователю?"
        await bot.send_photo(chat_id=develop_ids[0], photo=message.photo[-1].file_id, caption=text_message,
                             reply_markup=keyboard_for_develop.as_markup())
    else:
        text_message = "<b>Сообщение от пользователя: </b>" + message.text + "\n" + \
                       f"user_id: {message.from_user.id}" + "\nХотите ответить пользователю?"
        await bot.send_message(chat_id=develop_ids[0], text=text_message, reply_markup=keyboard_for_develop.as_markup())
    await message.reply("Твой запрос отправлен разработчику!", reply_markup=profile_keyboard)
    await state.clear()