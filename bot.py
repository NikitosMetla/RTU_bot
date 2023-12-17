from aiogram import Dispatcher, Bot
from handlers import user_router, develop_router, admin_router, main_admin_router, headman_router
from handlers.user import (auth, profile, communicate_develop,
                           greetings, cleaning_schedule, communicate_comendant, call_friends)
import asyncio
from data.settings import token, storage
from handlers.user.Seelling_things import selling_things, my_things, list_things


async def main():
    bot = Bot(token=token, parse_mode="html")
    print(await bot.get_me())
    await bot.delete_webhook(drop_pending_updates=True)
    dp = Dispatcher(storage=storage)
    dp.include_routers(auth.auth_router, greetings.greeting_router, profile.profile_router,
                       cleaning_schedule.cleaning_router, communicate_develop.com_develop_router,
                       communicate_comendant.com_comendant_router, selling_things.selling_router, my_things.my_thigs_router,
                       list_things.list_things_router, call_friends.call_friends_router,
                       develop_router.router, admin_router.router, main_admin_router.main_admin_router,
                       headman_router.headman_router, call_friends.end_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())