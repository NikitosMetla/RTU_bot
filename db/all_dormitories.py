import json


class Dormitory:
    def __init__(self, obchaga: str | int | None = "",
                 floor: str | int | None = "",
                 user: str | None = ""):
        self.obchaga = str(obchaga)
        self.floor = str(floor)
        self.user = user
        with open("C:/Users/Nikita/Downloads/Telegram Desktop/MIREA_bot/MIREA_bot_test/data/all_dormitories.json",
                  "r", encoding="utf-8") as dormitories:
            self.dormitories = json.load(dormitories)

    async def add_student(self, user_id: int| str, room: str | int):
        user_id = str(user_id)
        room = str(room)
        my_room = self.dormitories.get(self.obchaga).get("students").get(self.floor).get(room)
        if my_room is None:
            self.dormitories[self.obchaga]["students"][self.floor][room] = []
            my_room = []
        if user_id not in my_room:
            self.dormitories[self.obchaga]["students"][self.floor][room].append(user_id)
            self.save_data()

    async def add_starosta(self, user_id: int | str, initials: str):
        user_id = str(user_id)
        self.dormitories[self.obchaga]["headmans"][self.floor][user_id] = initials
        self.save_data()

    async def delete_starosta(self, user_id: int | str):
        user_id = str(user_id)
        self.dormitories[self.obchaga]["headmans"][self.floor].pop(user_id)
        self.save_data()

    async def add_admin(self, user_id: int | str, initials: str):
        user_id = str(user_id)
        self.dormitories[self.obchaga]["admins"][user_id] = initials
        self.save_data()

    async def student_in_obchaga(self, user_id, room: str | int):
        room = self.dormitories.get(self.obchaga).get("students").get(self.floor).get(room)
        if room:
            if user_id in room:
                return True
        return False

    async def get_obchaga_students(self):
        dormitory = self.dormitories.get(self.obchaga).get("students")
        students = []
        for floor in dormitory.keys():
            for room in dormitory.get(floor).keys():
                for user in dormitory.get(floor).get(room):
                    students.append(user)
        return students

    async def headmans_in_obchaga(self, user_id):
        headmans_on_floor = self.dormitories.get(self.obchaga).get("headmans").get(self.floor).get(user_id)
        if headmans_on_floor:
            return True
        return False

    async def admin_in_obchaga(self, user_id):
        user_id = str(user_id)
        admin_in_obchaga = self.dormitories.get(self.obchaga).get("admins")
        if user_id in admin_in_obchaga:
            return True
        return False

    async def get_headman(self):
        return self.dormitories.get(self.obchaga).get("headmans").get(self.floor)

    async def get_obchaga_admins(self):
        return self.dormitories.get(self.obchaga).get("admins")

    async def get_floors(self):
        return list(self.dormitories.get(self.obchaga).get("students").keys())

    async def is_admin(self, user_id):
        for dormitory in self.dormitories.keys():
            if str(user_id) in list(self.dormitories.get(dormitory).get("admins").keys()):
                return True
        return False

    async def is_headman(self, user_id):
        for dormitory in self.dormitories.keys():
            for floor in self.dormitories.get(dormitory).get("headmans").keys():
                if str(user_id) in list(self.dormitories.get(dormitory).get("headmans").get(floor).keys()):
                    return True
        return False

    async def add_security(self, security_id):
        self.dormitories[self.obchaga]["security"] = security_id
        self.save_data()

    async def get_obchaga_security(self):
        return self.dormitories.get(self.obchaga).get("security")

    async def add_moderator(self, security_id):
        self.dormitories[self.obchaga]["moderators"].append(security_id)
        self.save_data()

    async def get_moderators(self):
        return self.dormitories.get(self.obchaga).get("moderators")

    async def delete_moderators(self, moderator_id):
        self.dormitories[self.obchaga]["moderators"].remove(moderator_id)

    def save_data(self):
        with open("C:/Users/Nikita/Downloads/Telegram Desktop/MIREA_bot/MIREA_bot_test/data/all_dormitories.json",
                  "w", encoding="utf-8") as obchagas:
            json.dump(self.dormitories, obchagas, indent=2)