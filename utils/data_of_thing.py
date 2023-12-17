from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class CreateThing:
    def __init__(self, category, user_id, thing_id):
        self.category = category
        self.user_id = user_id
        self.thing_id = thing_id

    async def data_thing_keyboard(self):
        data_of_thing = InlineKeyboardBuilder()
        data_of_thing.row(InlineKeyboardButton(text="Изменить категорию", callback_data=f"edit_category|{self.category}"
                                                                                        f"|{self.user_id}|{self.thing_id}"))
        data_of_thing.row(InlineKeyboardButton(text="Название вещи", callback_data=f"name|{self.category}|{self.user_id}"
                                                                                   f"|{self.thing_id}"))
        data_of_thing.row(InlineKeyboardButton(text="Цена", callback_data=f"price|{self.category}|{self.user_id}|"
                                                                          f"{self.thing_id}"))
        data_of_thing.row(InlineKeyboardButton(text="Состояние", callback_data=f"state|{self.category}|{self.user_id}|"
                                                                               f"{self.thing_id}"))
        data_of_thing.row(InlineKeyboardButton(text="Описание", callback_data=f"description|{self.category}|"
                                                                              f"{self.user_id}|{self.thing_id}"))
        data_of_thing.row(InlineKeyboardButton(text="Фотографии", callback_data=f"photo|{self.category}|"
                                                                                f"{self.user_id}|{self.thing_id}"))
        data_of_thing.row(InlineKeyboardButton(text="Отправить на модерацию", callback_data=f"Отправить|{self.category}|"
                                                                                            f"{self.user_id}|"
                                                                                            f"{self.thing_id}"))
        return data_of_thing

    async def edit_thing_keyboard(self):
        user_thing = InlineKeyboardBuilder()
        user_thing.row(InlineKeyboardButton(text=f"Редактировать", callback_data=f"edit_thing|{self.category}|"
                                                                                 f"{self.user_id}|{self.thing_id}|"))
        user_thing.row(InlineKeyboardButton(text=f"Удалить объявление", callback_data=f"delete_thing|{self.category}|"
                                                                                      f"{self.user_id}|{self.thing_id}|"))
        user_thing.row(InlineKeyboardButton(text="🔙Назад к моим объявлениям", callback_data="back_to_things"))
        return user_thing