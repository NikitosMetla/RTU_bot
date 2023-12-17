from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db.all_dormitories import Dormitory


class Floors:
    def __init__(self, obchaga, floor: str | int | None = ""):
        self.obchaga = obchaga
        self.floor = floor

    async def generate_keyboard(self):
        floors_keyboard = InlineKeyboardBuilder()
        dormitory = await Dormitory(self.obchaga).get_floors()
        for floor in range(0, len(dormitory) - 1, 2):
            floors_keyboard.row(types.InlineKeyboardButton(text=f"{dormitory[floor]} этаж",
                                                           callback_data=f"floor|{dormitory[floor]}|{self.obchaga}"),
                                types.InlineKeyboardButton(text=f"{dormitory[floor + 1]} этаж",
                                                           callback_data=f"floor|{dormitory[floor + 1]}|{self.obchaga}"))
        if len(dormitory) % 2 != 0:
            floors_keyboard.row(types.InlineKeyboardButton(text=f"{dormitory[-1]} этаж",
                                                           callback_data=f"floor|{dormitory[-1]}|{self.obchaga}"))
        floors_keyboard.row(types.InlineKeyboardButton(text="Назад к выбору действий", callback_data="main_admin"))
        return floors_keyboard

    async def list_headmans(self):
        headmans_keyboard = InlineKeyboardBuilder()
        headmans = await Dormitory(obchaga=self.obchaga, floor=self.floor).get_headman()
        for headman in headmans.keys():
            initials = headmans.get(headman)
            headmans_keyboard.row(types.InlineKeyboardButton(text=initials,
                                                             callback_data=f"del_head|{self.obchaga}"
                                                                           f"|{self.floor}|{headman}"))
        return headmans_keyboard
