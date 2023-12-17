from aiogram import Bot, types
from aiogram import Router
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import any_state

from data.keyboards import profile_keyboard, cancel_keyboard, headman_keyboard

headman_router = Router()


@headman_router.message(Text(text="/headman"), any_state)
async def main_admin(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Привествуем, выберите свои дальнейшие действия!",
                         reply_markup=headman_keyboard.as_markup())
