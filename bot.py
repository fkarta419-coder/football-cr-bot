import os
import random
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from players import PLAYERS
from keep_alive import keep_alive


TOKEN = os.getenv("8944917133:AAHzyZPUwfVahJEko0gOapBGh0nCxjcDcmY")

if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN не найден")


bot = Bot(token=TOKEN)
dp = Dispatcher()

games = {}


def new_player(user_id):
    player = random.choice(PLAYERS)
    games[user_id] = player
    return player


@dp.message(Command("start"))
async def start(message: Message):
    player = new_player(message.from_user.id)

    await message.answer(
        "⚽ УГАДАЙ ИГРОКА\n\n"
        f"🌍 Нация: {player['nation']}\n"
        f"⭐ Рейтинг: {player['rating']}\n"
        f"⚽ Позиция: {player['position']}\n\n"
        "Кто это?"
    )


@dp.message(Command("new"))
async def new_game(message: Message):
    player = new_player(message.from_user.id)

    await message.answer(
        "🔄 НОВЫЙ РАУНД\n\n"
        f"🌍 Нация: {player['nation']}\n"
        f"⭐ Рейтинг: {player['rating']}\n"
        f"⚽ Позиция: {player['position']}\n\n"
        "Кто это?"
    )


@dp.message()
async def answer(message: Message):
    user_id = message.from_user.id

    if user_id not in games:
        await message.answer("❗ Сначала напиши /start")
        return

    player = games[user_id]

    answer = message.text.strip().lower()
    correct = player["name"].lower()

    if answer == correct:
        await message.answer(
            f"🎉 ПРАВИЛЬНО!\n\n"
            f"⚽ Это {player['name']}!"
        )

        new_player_data = new_player(user_id)

        await message.answer(
            "🔄 НОВЫЙ РАУНД\n\n"
            f"🌍 Нация: {new_player_data['nation']}\n"
            f"⭐ Рейтинг: {new_player_data['rating']}\n"
            f"⚽ Позиция: {new_player_data['position']}\n\n"
            "Кто это?"
        )

    else:
        await message.answer("❌ Неправильно! Попробуй ещё раз.")


async def main():
    keep_alive()

    print("Бот запущен!")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
