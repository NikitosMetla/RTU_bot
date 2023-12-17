from aiogram import types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

cancel_keyboard = InlineKeyboardBuilder()
cancel_keyboard.row(InlineKeyboardButton(text="Отмена❌", callback_data="Отмена❌"))


inline_add_data_keyboard = InlineKeyboardBuilder()
inline_add_data_keyboard.row(types.InlineKeyboardButton(text='Вернуться в личный кабинет', callback_data='get_profile'))

types.KeyboardButton(text="Забыл код"), types.KeyboardButton(text="Отмена❌")
restore_keyboard = InlineKeyboardBuilder()
restore_keyboard.row(InlineKeyboardButton(text="Забыл код", callback_data="forget_code"))
restore_keyboard.row(InlineKeyboardButton(text="Отмена❌", callback_data="Отмена❌"))


# buy_or_sell_kb = [
#         [types.KeyboardButton(text="Посмотреть объявленияℹ📋"), types.KeyboardButton(text="Продать💰")],
#         [types.KeyboardButton(text="Отмена❌"), types.KeyboardButton(text="Мои объявления🟢")]
#     ]
# buy_or_sell_keyboard = types.ReplyKeyboardMarkup(keyboard=buy_or_sell_kb, resize_keyboard=True)
buy_or_sell_keyboard = InlineKeyboardBuilder()
buy_or_sell_keyboard.row(InlineKeyboardButton(text="Посмотреть объявленияℹ📋", callback_data="view_things"))
buy_or_sell_keyboard.row(InlineKeyboardButton(text="Продать💰", callback_data="sell_thing"))
buy_or_sell_keyboard.row(InlineKeyboardButton(text="Мои объявления🟢", callback_data="my_things"))
buy_or_sell_keyboard.row(InlineKeyboardButton(text="Отмена❌", callback_data="Отмена❌"))


profile_kb = [
        [KeyboardButton(text='Личный кабинет')],
        [KeyboardButton(text="График уборкиℹ️"), KeyboardButton(text="Позвать друга🔶")],
        [KeyboardButton(text="Связь с комендантом💬"), KeyboardButton(text="Связь с разработчиками💬")],
        [KeyboardButton(text="Барахолка💵")]
    ]
profile_keyboard = ReplyKeyboardMarkup(keyboard=profile_kb, resize_keyboard=True)


categories_keyboard = InlineKeyboardBuilder()
categories_keyboard.row(InlineKeyboardButton(text="Техника📱", callback_data="Техника📱"))
categories_keyboard.row(InlineKeyboardButton(text="Канцелярия", callback_data="Канцелярия"))
categories_keyboard.row(InlineKeyboardButton(text="Одежда👕", callback_data="Одежда👕"))
categories_keyboard.row(InlineKeyboardButton(text="Спорт🏃‍♀️", callback_data="Спорт🏃‍♀️"))
categories_keyboard.row(InlineKeyboardButton(text="Другое🔵", callback_data="Другое🔵"))
categories_keyboard.row(InlineKeyboardButton(text="🔙Назад на начальную страницу", callback_data="back_to_startpage"))


categories = ["Техника📱", "Канцелярия", "Одежда👕", "Спорт🏃‍♀️", "Другое🔵"]


check_in_cleaning = InlineKeyboardBuilder()
check_in_cleaning.row(InlineKeyboardButton(text="Посмотреть свой график📅", callback_data="Посмотреть свой график📅"))
check_in_cleaning.row(InlineKeyboardButton(text="Начать уборку▶️", callback_data="Начать уборку▶️"))




start_kb = [
    [KeyboardButton(text="Авторизация")]
]

start_keyboard = ReplyKeyboardMarkup(keyboard=start_kb, resize_keyboard=True)


main_admin_keyboard = InlineKeyboardBuilder()
main_admin_keyboard.row(InlineKeyboardButton(text="Выложить объявление", callback_data="post_information"))
main_admin_keyboard.row(InlineKeyboardButton(text="Добавить старосту этажа", callback_data="new_headman"))
main_admin_keyboard.row(InlineKeyboardButton(text="Удалить старосту этажа", callback_data="delete_headman"))
main_admin_keyboard.row(InlineKeyboardButton(text="Добавить коменданта", callback_data="new_admin"))
main_admin_keyboard.row(InlineKeyboardButton(text="Добавить/изменить охранника", callback_data="new_security"))


dormitories_keyboard = InlineKeyboardBuilder()
dormitories_keyboard.row(InlineKeyboardButton(text="Первое общежитие", callback_data="obchaga|1"),
                         InlineKeyboardButton(text="Второе общежитие", callback_data="obchaga|2"))
dormitories_keyboard.row(InlineKeyboardButton(text="Третье общежитие", callback_data="obchaga|3"),
                         InlineKeyboardButton(text="Четвертое общежитие", callback_data="obchaga|4"))
dormitories_keyboard.row(InlineKeyboardButton(text="Пятое общежитие", callback_data="obchaga|5"),
                         InlineKeyboardButton(text="Шестое общежитие", callback_data="obchaga|6"))
dormitories_keyboard.row(InlineKeyboardButton(text="Назад к выбору действий", callback_data="main_admin"))


choise_obchaga = InlineKeyboardBuilder()
choise_obchaga.row(InlineKeyboardButton(text="Для первого общежития", callback_data="post|obchaga|1"))
choise_obchaga.row(InlineKeyboardButton(text="Для второго общежития", callback_data="post|obchaga|2"),
                   InlineKeyboardButton(text="Для третьего общежития", callback_data="post|obchaga|3"))
choise_obchaga.row(InlineKeyboardButton(text="Для четвертого общежития", callback_data="post|obchaga|4"),
                   InlineKeyboardButton(text="Для пятого общежития", callback_data="post|obchaga|5"))
choise_obchaga.row(InlineKeyboardButton(text="Назад к выбору действий", callback_data="main_admin"))

back_to_obchaga = InlineKeyboardBuilder()
back_to_obchaga.row(InlineKeyboardButton(text="Назад к выбору общежитий", callback_data="post_information"))


back_to_graphic = InlineKeyboardBuilder()
back_to_graphic.row(InlineKeyboardButton(text="Назад к выбору действий", callback_data="graphic_cleaning"))

back_choise_obchaga = InlineKeyboardBuilder()
back_choise_obchaga.row(InlineKeyboardButton(text="Назад к выбору общежития", callback_data="new_admin_obchaga"))


headman_keyboard = InlineKeyboardBuilder()
headman_keyboard.row(InlineKeyboardButton(text="Просмотр графика уборки на этаже",
                                          callback_data="cleaning_schedule_for_headman"))
headman_keyboard.row(InlineKeyboardButton(text="Изменить график уборки одной из комнат",
                                          callback_data="edit_schedule_room"))