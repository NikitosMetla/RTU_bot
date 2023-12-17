import json


class Guests:
    def __init__(self, user_id: str | int or None = "", application_id: str | int | None = ""):
        self.user_id = str(user_id)
        self.application_id = application_id
        with open("C:/Users/Nikita/Downloads/Telegram Desktop/MIREA_bot/MIREA_bot_test/data/guests_applications.json",
                  "r", encoding="utf-8") as users:
            self.users = json.load(users)

    async def add_application(self, friend_initials, date, time):
        if self.users.get(self.user_id) is None:
            self.users[self.user_id] = {}
            self.application_id = self.user_id + "|" + "1"
        else:
            self.application_id = self.user_id + "|" + str(len(list(self.users.get(self.user_id).keys())) + 1)
        self.users[self.user_id][self.application_id] = {
            "friend_initials": friend_initials,
            "date": date,
            "time": time,
            "confirm": False
        }
        self.save_data()

    async def get_friends_initials(self) -> str:
        return self.users.get(self.user_id).get(self.application_id).get("friend_initials")

    async def get_date(self) -> str:
        return self.users.get(self.user_id).get(self.application_id).get("date")

    async def get_time(self) -> str:
        return self.users.get(self.user_id).get(self.application_id).get("time")

    async def get_confirm(self) -> bool:
        return self.users.get(self.user_id).get(self.application_id).get("confirm")

    async def get_user_application(self, application_id) -> dict:
        return self.users.get(self.user_id).get(application_id)

    async def edit_cofirm_guests(self):
        self.users[self.user_id][self.application_id]["confirm"] = True
        self.save_data()

    async def delete_guests(self):
        self.users[self.user_id].pop(self.application_id)
        self.save_data()

    def save_data(self):
        with open("C:/Users/Nikita/Downloads/Telegram Desktop/MIREA_bot/MIREA_bot_test/data/guests_applications.json",
                  "w", encoding="utf-8") as users:
            json.dump(self.users, users, indent=2)