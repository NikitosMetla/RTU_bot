from aiogram import types
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

token = "6378983053:AAEx3n6CE1K_XUk9ApWsDXikJLp61gLCCGA"
storage = MemoryStorage()


categories = ["Техника📱", "Канцелярия", "Одежда👕", "Спорт🏃‍♀️", "Другое🔵"]


class InputMessage(StatesGroup):
    comment_to_thing = State()
    enter_description = State()
    enter_state = State()
    message_to_developer = State()
    answer_to_user = State()
    calling_guests = State()
    time_guests = State()
    code_confirm = State()
    enter_email = State()
    enter_password = State()
    enter_code = State()
    message_to_comendant = State()
    comendant_to_user = State()
    choice_category = State()
    get_things = State()
    get_photo = State()
    new_thing = State()
    get_thing = State()
    enter_category = State()
    edit_category = State()
    enter_name = State()
    enter_price = State()
    input_email = State()
    input_password = State()
    input_user_data = State()
    enter_post_information = State()
    choise_obchaga_headman = State()
    choise_floor_headman = State()
    enter_headman_ID = State()
    enter_headman_initials = State()
    choise_del_headman = State()
    enter_admin_ID = State()
    enter_admin_initials = State()
    new_security = State()
    enter_security_ID = State()
    enter_code2 = State()
    enter_email2 = State()
    enter_password2 = State()
    enter_comment_request = State()


develop_ids = [774127719, 123456789]
moderators = [774127719]

comendant_ids = {1: {123123: 774127719}}