import math

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List

from db.user_things import Things


class Paginator(object):
    def __init__(self, data: dict or None = {}, category: str or None = ""):
        self.category = category
        self.data: List[dict] = []
        for user_id in data.keys():
            for thing_id in data.get(user_id).keys():
                if data.get(user_id).get(thing_id).get('verified'):
                    self.data.append(data.get(user_id).get(thing_id))
                    self.data[-1]["thing_id"] = thing_id
                    self.data[-1]['user_id'] = user_id
                continue

    async def generate_things_list_keyboard(self, page:  int = 0):
        if page >= math.ceil(len(self.data) / 5) and page != 0:
            page = math.ceil(len(self.data) / 5) - 1
        if len(self.data) == 0:
            page = 0
        keyboard = InlineKeyboardBuilder()
        for number, item in enumerate(self.data[page * 5:page * 5 + 5]):
            callback_data = f'get_thing|{item.get("thing_id")}|{item.get("user_id")}|{self.category}'
            keyboard.row(InlineKeyboardButton(text=item.get("name"), callback_data=callback_data))
        number_pages = math.ceil(len(self.data) / 5) if len(self.data) > 0 else 1
        keyboard.row(InlineKeyboardButton(text="⬅️", callback_data=f"things_list|page_back|{page}|{self.category}"),
                     InlineKeyboardButton(text=f"{page + 1}/{number_pages}",
                                          callback_data=f"things_list|page_now|{page}|{self.category}"),
                     InlineKeyboardButton(text="➡️", callback_data=f"things_list|page_next|{page}|{self.category}"))
        keyboard.row(InlineKeyboardButton(text='🔙 Назад в выбор категорий', callback_data='get_categories'))
        return keyboard

    async def generate_my_things_keyboard(self, user_id: str or int, page: int = 0):
        user_id = str(user_id)
        things = await Things(user_id=user_id).get_my_thing()
        keyboard = InlineKeyboardBuilder()
        if page >= math.ceil(len(things) / 5) and page != 0:
            page = math.ceil(len(things) / 5) - 1
        if len(things) == 0:
            page = 0
        for number, item in enumerate(things[page * 5:page * 5 + 5]):
            callback_data = f'my_thing|{item.get("thing_id")}|{user_id}|{item.get("category")}'
            if not (item.get("verified")):
                keyboard.row(InlineKeyboardButton(text=f'{item.get("name")}\n(Не выложено)', callback_data=callback_data))
            else:
                keyboard.row(InlineKeyboardButton(text=item.get("name"), callback_data=callback_data))
        number_pages = math.ceil(len(things) / 5) if len(things) > 0 else 1
        keyboard.row(InlineKeyboardButton(text="⬅️", callback_data=f"my_things|page_back|{page}|{self.category}"),
                     InlineKeyboardButton(text=f"{page + 1}/{number_pages}",
                                          callback_data=f"my_things|page_now|{page}|{self.category}"),
                     InlineKeyboardButton(text="➡️", callback_data=f"my_things|page_next|{page}|{self.category}"))
        keyboard.row(
            InlineKeyboardButton(text="🔙Назад на начальную страницу", callback_data="back_to_startpage"))
        return keyboard