import json


class Users:
    def __init__(self, user_id: str | int | None = ""):
        self.user_id: str = str(user_id)
        with open("data/user_auth.json", "r", encoding='utf-8') as user_ids:
            self.user_ids: dict = json.load(user_ids)

    async def add_new_user(self,
                     obchaga: int | None,
                     room: int | None,
                     email: str,
                     password: str,
                     secret_code: int | None,
                     id_floor: int | None,
                     cookies: dict | None,
                     initials: str,
                     auth=True):
        self.user_ids[self.user_id] = {
            "is_auth": auth,
            "initials": initials,
            "id_obchaga": obchaga,
            "id_room": room,
            'id_floor': id_floor,
            'secret_code': secret_code,
            "email": email,
            "password": password,
            "cookies": cookies
        }
        await self.save_data()

    async def check_user(self):
        return self.user_ids.get(self.user_id)

    async def get_cookies(self) -> dict:
        return self.user_ids.get(self.user_id).get('cookies')

    async def get_auth(self) -> bool:
        if not self.user_ids.get(self.user_id):
            return False
        return self.user_ids.get(self.user_id).get("is_auth")

    async def get_all_ids(self) -> list:
        return list(self.user_ids.keys())

    async def get_number_of_obchaga(self) -> int:
        return self.user_ids.get(self.user_id).get("id_obchaga")

    async def get_room(self) -> int:
        return self.user_ids.get(self.user_id).get("id_room")

    async def get_initials(self) -> str:
        return self.user_ids.get(self.user_id).get("initials")

    async def get_email(self) -> str:
        return self.user_ids.get(self.user_id).get("email")

    async def get_password(self) -> str:
        return self.user_ids.get(self.user_id).get("password")

    async def get_floor(self):
        return self.user_ids.get(self.user_id).get("id_floor")

    async def get_code(self):
        return self.user_ids.get(self.user_id).get("secret_code")

    async def add_id_room(self, number: int | str):
        self.user_ids[self.user_id]['id_room'] = int(number)
        await self.save_data()

    async def add_id_floor(self, number: int | str):
        self.user_ids[self.user_id]['id_floor'] = int(number)
        await self.save_data()

    async def add_secret_code(self, code: str | int):
        self.user_ids[self.user_id]["secret_code"] = int(code)
        await self.save_data()

    async def add_number_for_obchaga(self,  number: int | str):
        self.user_ids[self.user_id]['id_obchaga'] = int(number)
        await self.save_data()

    async def add_user_initials(self,  initials: str):
        self.user_ids[self.user_id]['initials'] = initials
        self.save_data()

    async def save_data(self):
        with open("data/user_auth.json", "w", encoding='utf-8') as user_ids:
            json.dump(self.user_ids, user_ids, indent=2)

