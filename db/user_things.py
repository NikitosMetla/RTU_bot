import json
import asyncio


class Things:
    def __init__(self, category: str or None = "", thing_id: str or int or None = "", user_id: str or int or None = None):
        self.category = category
        self.thing_id = thing_id
        self.user_id = str(user_id) if user_id else None
        with open("data/users_things.json", "r", encoding="utf-8") as user_things:
            self.user_things = json.load(user_things)
        # print(self.user_things)

    async def add_thing(self, user_id: str or int, user_name: str, name: str or None = "Не вводилось",
                        price: int or str or None = "Не вводилось", state_thing: str or None = "",
                        description: str or None = "", photo_ids: list or None = [], verified: bool or None = False):
        self.user_id = str(user_id)
        user = self.user_things.get(self.category).get(self.user_id)
        if user is None:
            self.user_things[self.category][self.user_id] = {}
            user = {}
        if self.thing_id == "":
            self.thing_id = self.user_id + "/" + str(len(self.user_things.get(self.category).get(self.user_id).keys()) + 1)
        user[self.thing_id] = {
            "user_name": user_name,
            "name": name,
            "state_thing": state_thing,
            "price": price,
            "description": description,
            "photo_ids": photo_ids,
            "thing_id": self.thing_id,
            "verified": verified
        }
        self.user_things[self.category][self.user_id] = user
        self.save_data()

    async def get_user_name(self):
        return self.user_things.get(self.category).get(self.user_id).get(self.thing_id).get("user_name")

    async def delete_thing(self):
        self.user_things[self.category][self.user_id].pop(self.thing_id)
        self.save_data()

    async def get_my_thing(self):
        user_things = self.user_things
        my_things = []
        for category in user_things.keys():
            if len(user_things.get(category).keys()) == 0:
                continue
            users_ids = list(user_things.get(category).keys())
            key = 0
            user_id = users_ids[key]
            things_of_user = user_things.get(category)
            while user_id != self.user_id and ((len(users_ids) - 1) >= (key + 1)):
                key += 1
                continue
            else:
                user_id = users_ids[key]
                if key == (len(users_ids) - 1) and user_id != self.user_id:
                    continue
                user_id = users_ids[key]
                for thing_id in things_of_user.get(user_id).keys():
                    things_of_user[user_id][thing_id]["category"] = category
                    my_things.append(things_of_user.get(user_id).get(thing_id))
        return my_things

    async def get_category(self):
        return self.user_things.get(self.category).get(self.user_id).get(self.thing_id)

    async def get_thing_data(self):
        print(self.user_things.get(self.category).get(self.user_id).get(self.thing_id))
        return self.user_things.get(self.category).get(self.user_id).get(self.thing_id)

    async def edit_thing_data(self, thing_data: dict):
        self.user_things[self.category][self.user_id][self.thing_id] = thing_data
        self.save_data()

    async def get_name(self):
        return self.user_things.get(self.category).get(self.user_id).get(self.thing_id).get("name")

    async def get_verified(self):
        return self.user_things.get(self.category).get(self.user_id).get(self.thing_id).get("verified")

    async def get_thing_id(self):
        return self.user_things.get(self.category).get(self.user_id).get(self.thing_id).get("thing_id")

    async def get_photos(self):
        return self.user_things.get(self.category).get(self.user_id).get(self.thing_id).get("photo_ids")

    async def get_state_thing(self):
        return self.user_things.get(self.category).get(self.user_id).get(self.thing_id).get("state_thing")

    async def get_price(self):
        return self.user_things.get(self.category).get(self.user_id).get(self.thing_id).get("price")

    async def get_description(self):
        return self.user_things.get(self.category).get(self.user_id).get(self.thing_id).get("description")

    async def edit_name(self, new_name):
        self.user_things[self.category][self.user_id][self.thing_id]["name"] = new_name
        self.save_data()

    async def edit_verified(self, verified: bool):
        if verified:
            self.user_things[self.category][self.user_id][self.thing_id]["verified"] = True
        else:
            self.user_things[self.category][self.user_id][self.thing_id]["verified"] = False
        self.save_data()

    async def edit_state_thing(self, new_state_thing):
        self.user_things[self.category][self.user_id][self.thing_id]["state_thing"] = new_state_thing
        self.save_data()

    async def edit_price(self, new_price):
        self.user_things[self.category][self.user_id][self.thing_id]["price"] = new_price
        self.save_data()

    async def edit_description(self, new_description):
        self.user_things[self.category][self.user_id][self.thing_id]["description"] = new_description
        self.save_data()

    def save_data(self):
        with open("data/users_things.json", "w", encoding="utf-8") as things:
            json.dump(self.user_things, things, indent=2)

#
# async def main():
#     for i in range(10):
#         auth = Things("Техника")
#         await auth.add_thing(f"3245234523{i}", f"huy{i}",
#                              "sex",
#                              "12341234",
#                              "askdjfkjlasdflkas;kdfkasdpjf",
#                              ["AgACAgIAAxkBAAIGYmTUIL-E3kNtQYA156x3QUxtRW_CAAIWyjEbde2oSgTc08OiGMh0AQADAgADeQADMAQ",
#                               "AgACAgIAAxkBAAIGY2TUINOsTAcXqidRWT9Lv6iJBpKGAAIXyjEbde2oStRaIMILlB42AQADAgADeQADMAQ",
#                               "AgACAgIAAxkBAAIGZGTUINV2efa-uVYUUfnPnsmO_gE5AAIYyjEbde2oSmqNlm4j9nsaAQADAgADeQADMAQ",
#                               "AgACAgIAAxkBAAIGZWTUINdqItnajMFVI4lMgTHrYDIjAAIZyjEbde2oSu6n8EX7FMfDAQADAgADeQADMAQ"])
#
# asyncio.run(main())