import json


class Request:
    def __init__(self, obchaga: str | int | None = "",
                 user_id: str | int | None = "",
                 floor: str | int | None = "",
                 room: str | int | None = ""):
        self.obchaga, self.user_id, self.floor, self.room = str(obchaga), str(user_id), str(floor), str(room)
        with open("C:/Users/Nikita/Downloads/Telegram Desktop/MIREA_bot/MIREA_bot_test/"
                  "data/students_requests_for_admins.json",
                  "r", encoding="utf-8") as requests:
            self.requests = json.load(requests)
        self.request_id = self.obchaga + "/" + str(len(list(self.requests.get(self.obchaga).keys())) + 1)

    async def add_request(self, text_request: str,
                          messages_for_admins: dict,
                          date: str,
                          photo_id: str | int | None = ""):
        self.requests[self.obchaga][self.request_id] = {
            "user_id": self.user_id,
            "floor": self.floor,
            "room": self.room,
            "text_request": text_request,
            "messages_for_admins": messages_for_admins,
            "photo_id": photo_id,
            "date_adoption": date,
            "processing": False,
            "handler": None,
            "announce_acceptance": False,
            "date_treatment": None,
            "admin_text": None
        }
        self.save_data()

    async def get_request_data(self, request_id):
        return self.requests.get(self.obchaga).get(request_id)

    async def get_request_student_id(self, request_id):
        return self.requests.get(self.obchaga).get(request_id).get("user_id")

    async def get_request_text(self, request_id):
        return self.requests.get(self.obchaga).get(request_id).get("text_request")

    async def get_messages_for_admins(self, request_id):
        return self.requests.get(self.obchaga).get(request_id).get("messages_for_admins")

    async def get_date_adoption(self, request_id):
        return self.requests.get(self.obchaga).get(request_id).get("date_adoption")

    async def edit_request_processing(self, request_id, admin_id, obchaga):
        self.requests[obchaga][request_id]["processing"] = True
        self.save_data()
        admin_id = str(admin_id)
        message_id = self.requests[obchaga][request_id]["messages_for_admins"].pop(admin_id)
        self.requests[obchaga][request_id]["handler"] = admin_id
        self.save_data()
        return self.requests.get(obchaga).get(request_id).get("messages_for_admins"), message_id

    async def add_date_treatment(self, date: str, request_id: str):
        self.requests[self.obchaga][request_id]["date_treatment"] = date
        self.save_data()

    async def get_date_of_processing(self, request_id):
        return self.requests.get(self.obchaga).get(request_id).get("date_treatment")

    async def add_admin_text(self, request_id, admin_text):
        self.requests[self.obchaga][request_id]["admin_text"] = admin_text
        self.save_data()

    async def announce_acceptance(self, request_id):
        self.requests[self.obchaga][request_id]["announce_acceptance"] = True
        self.save_data()

    async def edit_request_text(self, request_id, request_text):
        self.requests[self.obchaga][request_id]["text_request"] = request_text
        self.save_data()

    def save_data(self):
        with open("C:/Users/Nikita/Downloads/Telegram Desktop/MIREA_bot/MIREA_bot_test/"
                  "data/students_requests_for_admins.json",
                  "w", encoding="utf-8") as new_requests:
            json.dump(self.requests, new_requests, indent=2)

