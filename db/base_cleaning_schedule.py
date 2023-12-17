import asyncio
import json
import datetime


class Cleaning:
    def __init__(self, obchaga: str | int | None = "",
                 floor: str | int | None = "",
                 room: str | int | None = ""):
        self.obchaga = str(obchaga)
        self.floor = str(floor)
        self.room = str(room)
        with open("C:/Users/Nikita/Downloads/Telegram Desktop/MIREA_bot/MIREA_bot_test/data/base_cleaning_schedule.json",
                  "r", encoding="utf-8") as dormitories:
            self.dormitories = json.load(dormitories)

    async def add_information(self, day_week: str, time: str):
        self.dormitories[self.obchaga][self.floor][self.room] = {
            "day_week": day_week,
            "time": str(time)
        }
        self.save_data()

    async def delete_information(self):
        self.dormitories[self.obchaga][self.floor].pop(self.room)
        self.save_data()

    def save_data(self):
        with open("C:/Users/Nikita/Downloads/Telegram Desktop/MIREA_bot/MIREA_bot_test/data/base_cleaning_schedule.json",
                  "w", encoding="utf-8") as obchagas:
            json.dump(self.dormitories, obchagas, indent=2)


# async def main():
#     mamba = Cleaning(1, 1, 23)
#     await mamba.add_information(day_week="sunday", time="13:45")
#     mamba2 = Cleaning(1, 1, 34)
#     await mamba2.add_information(day_week="sunday", time="13:45")
#
# asyncio.run(main())
