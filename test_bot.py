import logging
from aiogram import Bot, types, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

API_TOKEN = ""
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dispatcher = Dispatcher(bot, storage=storage)


@dispatcher.message_handler(commands=['start'])
async def on_start(message: types.Message):
    # Создаем клавиатуру с кнопкой "Отправить местоположение"
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button = KeyboardButton("Отправить местоположение", request_location=True)
    keyboard.add(button)

    # Отправляем пользователю приветственное сообщение с клавиатурой
    await message.answer("Привет! Нажми кнопку, чтобы отправить местоположение.", reply_markup=keyboard)


@dispatcher.message_handler(content_types=[types.ContentType.LOCATION])
async def handle_location(message: types.Message):
    # Обработка полученных координат
    latitude = message.location.latitude
    longitude = message.location.longitude
    await message.reply(f"Вы отправили координаты: {latitude}, {longitude}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    from aiogram import executor

    executor.start_polling(dispatcher, skip_updates=True)
