import os
import random
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message


TOKEN = os.getenv("8944917133:AAHzyZPUwfVahJEko0gOapBGh0nCxjcDcmY")

if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN не найден")


bot = Bot(token=TOKEN)
dp = Dispatcher()


# =========================
# ИГРОКИ
# =========================

PLAYERS = [
    {"name": "Ламин Ямаль", "nation": "Испания", "rating": 89, "position": "RW"},
    {"name": "Рафинья", "nation": "Бразилия", "rating": 90, "position": "LW"},
    {"name": "Педри", "nation": "Испания", "rating": 88, "position": "CM"},
    {"name": "Гави", "nation": "Испания", "rating": 84, "position": "CM"},
    {"name": "Дани Ольмо", "nation": "Испания", "rating": 86, "position": "CAM"},
    {"name": "Жюль Кунде", "nation": "Франция", "rating": 87, "position": "CB"},
    {"name": "Лионель Месси", "nation": "Аргентина", "rating": 90, "position": "RW"},
    {"name": "Луис Суарес", "nation": "Уругвай", "rating": 84, "position": "ST"},
    {"name": "Родриго Де Пауль", "nation": "Аргентина", "rating": 82, "position": "CM"},
    {"name": "Серхио Регилон", "nation": "Испания", "rating": 78, "position": "LB"},
    {"name": "Тадео Альенде", "nation": "Аргентина", "rating": 75, "position": "RW"},
    {"name": "Тьяско Сеговия", "nation": "Аргентина", "rating": 74, "position": "CM"},
    {"name": "Гарри Кейн", "nation": "Англия", "rating": 90, "position": "ST"},
    {"name": "Джамал Мусиала", "nation": "Германия", "rating": 88, "position": "CAM"},
    {"name": "Майкл Олисе", "nation": "Франция", "rating": 85, "position": "RW"},

    {"name": "Килиан Мбаппе", "nation": "Франция", "rating": 91, "position": "ST"},
    {"name": "Винисиус Жуниор", "nation": "Бразилия", "rating": 90, "position": "LW"},
    {"name": "Джуд Беллингем", "nation": "Англия", "rating": 90, "position": "CAM"},
    {"name": "Федерико Вальверде", "nation": "Уругвай", "rating": 88, "position": "CM"},
    {"name": "Тибо Куртуа", "nation": "Бельгия", "rating": 89, "position": "GK"},
    {"name": "Антонио Рюдигер", "nation": "Германия", "rating": 86, "position": "CB"},
    {"name": "Эдуардо Камавинга", "nation": "Франция", "rating": 85, "position": "CM"},
    {"name": "Орельен Тчуамени", "nation": "Франция", "rating": 84, "position": "CDM"},
    {"name": "Ферлан Менди", "nation": "Франция", "rating": 84, "position": "LB"},
    {"name": "Дани Карвахаль", "nation": "Испания", "rating": 85, "position": "RB"},
    {"name": "Трент Александер-Арнольд", "nation": "Англия", "rating": 86, "position": "RB"},
    {"name": "Мохамед Салах", "nation": "Египет", "rating": 89, "position": "RW"},
    {"name": "Кевин Де Брёйне", "nation": "Бельгия", "rating": 87, "position": "CAM"},
    {"name": "Эрлинг Холанд", "nation": "Норвегия", "rating": 91, "position": "ST"},
    {"name": "Родри", "nation": "Испания", "rating": 91, "position": "CDM"},
]


# =========================
# ТЕКУЩИЙ ИГРОК
# =========================

games = {}


def new_round(user_id):
    player = random.choice(PLAYERS)

    games[user_id] = player

    return player


# =========================
# START
# =========================

@dp.message(Command("start"))
async def start(message: Message):

    player = new_round(message.from_user.id)

    await message.answer(
        "⚽ УГАДАЙ ИГРОКА\n\n"
        f"🌍 Нация: {player['nation']}\n"
        f"⭐ Рейтинг: {player['rating']}\n"
        f"⚽ Позиция: {player['position']}\n\n"
        "Кто это?"
    )


# =========================
# НОВЫЙ РАУНД
# =========================

@dp.message(Command("new"))
async def new_game(message: Message):

    player = new_round(message.from_user.id)

    await message.answer(
        "🔄 НОВЫЙ РАУНД\n\n"
        f"🌍 Нация: {player['nation']}\n"
        f"⭐ Рейтинг: {player['rating']}\n"
        f"⚽ Позиция: {player['position']}\n\n"
        "Кто это?"
    )


# =========================
# ОТВЕТ
# =========================

@dp.message()
async def answer(message: Message):

    user_id = message.from_user.id

    if user_id not in games:
        await message.answer(
            "❗ Сначала напиши /start"
        )
        return

    player = games[user_id]

    answer_text = message.text.strip().lower()
    correct_answer = player["name"].lower()

    if answer_text == correct_answer:

        await message.answer(
            f"🎉 ПРАВИЛЬНО!\n\n"
            f"⚽ Это {player['name']}!\n\n"
            "🔄 Новый игрок..."
        )

        new_player = new_round(user_id)

        await asyncio.sleep(0.5)

        await message.answer(
            f"🌍 Нация: {new_player['nation']}\n"
            f"⭐ Рейтинг: {new_player['rating']}\n"
            f"⚽ Позиция: {new_player['position']}\n\n"
            "Кто это?"
        )

    else:

        await message.answer(
            "❌ Неправильно!\n"
            "Попробуй ещё раз."
        )


# =========================
# ЗАПУСК
# =========================

async def main():

    print("Бот запущен!")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
