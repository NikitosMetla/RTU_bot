from aiogram import Bot, types
from aiogram import Router
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import any_state

from data.keyboards import profile_keyboard, cancel_keyboard
from data.settings import InputMessage

router = Router()


@router.callback_query(Text(contains='Ответить пользователю'), any_state)
async def answer_to_user(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(InputMessage.answer_to_user)
    await state.update_data(id=call.data[22:], cancel_message_id=call.message.message_id)
    await call.message.answer(f"Вы отвечаете пользователю с id: {call.data[22:]}", reply_markup=cancel_keyboard)


@router.callback_query(Text("No"), any_state)
async def answer_to_user(call: types.CallbackQuery):
    await call.message.delete()


@router.message(InputMessage.answer_to_user)
async def answering(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    if message.photo is not None:
        text_message = "<b>Сообщение от разработчика:\n</b>" + message.caption + "\n"
        await bot.send_photo(chat_id=data.get("id"), photo=message.photo[-1].file_id, caption=text_message,
                             reply_markup=profile_keyboard)
    else:
        text_message = "<b>Сообщение от разработчика:\n</b>" + message.text + "\n"
        await bot.send_message(chat_id=data.get("id"), text=text_message, reply_markup=profile_keyboard)
    await message.reply("Ваш ответ отправлен пользователю!")
    await bot.delete_message(chat_id=message.from_user.id, message_id=data.get("cancel_message_id"))
    await state.clear()