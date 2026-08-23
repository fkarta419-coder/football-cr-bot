import os
import random
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message


TOKEN = os.getenv("8944917133:AAHzyZPUwfVahJEko0gOapBGh0nCxjcDcmY")

if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN not found")


bot = Bot(token=TOKEN)
dp = Dispatcher()


PLAYERS = [
    {"name": "Ламин Ямаль", "nation": "Испания", "rating": 89, "position": "RW"},
    {"name": "Рафинья", "nation": "Бразилия", "rating": 90, "position": "LW"},
    {"name": "Педри", "nation": "Испания", "rating": 88, "position": "CM"},
    {"name": "Гави", "nation": "Испания", "rating": 84, "position": "CM"},
    {"name": "Лионель Месси", "nation": "Аргентина", "rating": 90, "position": "RW"},
    {"name": "Гарри Кейн", "nation": "Англия", "rating": 90, "position": "ST"},
    {"name": "Килиан Мбаппе", "nation": "Франция", "rating": 91, "position": "ST"},
    {"name": "Винисиус Жуниор", "nation": "Бразилия", "rating": 90, "position": "LW"},
    {"name": "Джуд Беллингем", "nation": "Англия", "rating": 90, "position": "CAM"},
    {"name": "Эрлинг Холанд", "nation": "Норвегия", "rating": 91, "position": "ST"},
]


games = {}


def new_round(user_id):
    player = random.choice(PLAYERS)
    games[user_id] = player
    return player


def question(player):
    return (
        "⚽ УГАДАЙ ИГРОКА\n\n"
        f"🌍 Нация: {player['nation']}\n"
        f"⭐ Рейтинг: {player['rating']}\n"
        f"⚽ Позиция: {player['position']}\n\n"
        "Кто это?"
    )


@dp.message(Command("start"))
async def start(message: Message):
    player = new_round(message.from_user.id)
    await message.answer(question(player))


@dp.message(Command("new"))
async def new_game(message: Message):
    player = new_round(message.from_user.id)
    await message.answer(question(player))


@dp.message()
async def answer(message: Message):
    user_id = message.from_user.id

    if user_id not in games:
        await message.answer("❗ Напиши /start")
        return

    player = games[user_id]

    if message.text.strip().casefold() == player["name"].casefold():
        await message.answer(
            f"🎉 ПРАВИЛЬНО!\n\n"
            f"⚽ Это {player['name']}!"
        )

        player = new_round(user_id)
        await message.answer(question(player))

    else:
        await message.answer("❌ Неправильно! Попробуй ещё раз.")


async def main():
    print("BOT STARTED")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
