import os
import random
import asyncio
import time
import sqlite3

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)


# =========================================================
# TOKEN
# =========================================================

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

print("TOKEN EXISTS:", bool(TOKEN))
print("TOKEN LENGTH:", len(TOKEN) if TOKEN else 0)

if not TOKEN:
    raise RuntimeError("TOKEN IS EMPTY")


bot = Bot(token=TOKEN)
dp = Dispatcher()


# =========================================================
# SETTINGS
# =========================================================

ROUND_TIME = 300

CHANNEL = "@LionelMessiG10AT"
CHANNEL_URL = "https://t.me/LionelMessiG10AT"


# =========================================================
# PLAYERS
# =========================================================

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
    {"name": "Виктор Осимхен", "nation": "Нигерия", "rating": 87, "position": "ST"},
    {"name": "Хвича Кварацхелия", "nation": "Грузия", "rating": 87, "position": "LW"},
    {"name": "Ашраф Хакими", "nation": "Марокко", "rating": 89, "position": "RB"},
    {"name": "Маркиньос", "nation": "Бразилия", "rating": 87, "position": "CB"},
    {"name": "Джанлуиджи Доннарумма", "nation": "Италия", "rating": 89, "position": "GK"},
    {"name": "Андре Онана", "nation": "Камерун", "rating": 83, "position": "GK"},
    {"name": "Бруну Фернандеш", "nation": "Португалия", "rating": 87, "position": "CAM"},
    {"name": "Бернарду Силва", "nation": "Португалия", "rating": 88, "position": "CAM"},
    {"name": "Рафаэл Леау", "nation": "Португалия", "rating": 86, "position": "LW"},
    {"name": "Криштиану Роналду", "nation": "Португалия", "rating": 90, "position": "ST"},
    {"name": "Виктор Дьёкереш", "nation": "Швеция", "rating": 87, "position": "ST"},
    {"name": "Александер Исак", "nation": "Швеция", "rating": 86, "position": "ST"},
    {"name": "Мартин Эдегор", "nation": "Норвегия", "rating": 87, "position": "CAM"},
    {"name": "Деклан Райс", "nation": "Англия", "rating": 87, "position": "CDM"},
    {"name": "Коул Палмер", "nation": "Англия", "rating": 87, "position": "CAM"},
    {"name": "Букайо Сака", "nation": "Англия", "rating": 87, "position": "RW"},
    {"name": "Фил Фоден", "nation": "Англия", "rating": 88, "position": "RW"},
    {"name": "Кай Хаверц", "nation": "Германия", "rating": 83, "position": "ST"},
    {"name": "Лерой Сане", "nation": "Германия", "rating": 84, "position": "RW"},
    {"name": "Флориан Вирц", "nation": "Германия", "rating": 89, "position": "CAM"},
    {"name": "Лаутаро Мартинес", "nation": "Аргентина", "rating": 89, "position": "ST"},
    {"name": "Хулиан Альварес", "nation": "Аргентина", "rating": 87, "position": "ST"},
    {"name": "Эмилиано Мартинес", "nation": "Аргентина", "rating": 86, "position": "GK"},
    {"name": "Алексис Макаллистер", "nation": "Аргентина", "rating": 86, "position": "CM"},
    {"name": "Энцо Фернандес", "nation": "Аргентина", "rating": 85, "position": "CM"},
    {"name": "Габриэл Мартинелли", "nation": "Бразилия", "rating": 84, "position": "LW"},
    {"name": "Габриэл Жезус", "nation": "Бразилия", "rating": 82, "position": "ST"},
    {"name": "Каземиро", "nation": "Бразилия", "rating": 84, "position": "CDM"},
    {"name": "Алиссон", "nation": "Бразилия", "rating": 89, "position": "GK"},
    {"name": "Эдерсон", "nation": "Бразилия", "rating": 88, "position": "GK"},
    {"name": "Тео Эрнандес", "nation": "Франция", "rating": 87, "position": "LB"},
    {"name": "Уильям Салиба", "nation": "Франция", "rating": 87, "position": "CB"},
    {"name": "Ибраима Конате", "nation": "Франция", "rating": 85, "position": "CB"},
    {"name": "Усман Дембеле", "nation": "Франция", "rating": 90, "position": "RW"},
]

# =========================================================
# GAME COMMANDS
# =========================================================

@dp.message(Command("kviz"))
async def kviz(message: Message):
    if not await require_subscription(message):
        return

    user_id = message.from_user.id

    register_user(
        user_id,
        message.from_user.username
    )

    # Удаляем старую игру
    games.pop(user_id, None)
    timers.pop(user_id, None)

    # Создаём новую игру
    player = new_round(user_id)

    print(f"KVIZ STARTED: {player['name']}")

    await message.answer(
        "🎮 НОВЫЙ РАУНД!\n\n" +
        question(player)
    )


# =========================================================
# NEW
# =========================================================

@dp.message(Command("new"))
async def new_game(message: Message):
    if not await require_subscription(message):
        return

    user_id = message.from_user.id

    register_user(
        user_id,
        message.from_user.username
    )

    games.pop(user_id, None)
    timers.pop(user_id, None)

    player = new_round(user_id)

    await message.answer(
        "🔄 НОВЫЙ РАУНД!\n\n" +
        question(player)
    )


# =========================================================
# STOP
# =========================================================

@dp.message(Command("stop"))
async def stop_game(message: Message):
    if not await require_subscription(message):
        return

    user_id = message.from_user.id

    player = games.pop(user_id, None)
    timers.pop(user_id, None)

    if player is None:
        await message.answer(
            "❌ У тебя нет активной игры."
        )
        return

    await message.answer(
        "🛑 ИГРА ОСТАНОВЛЕНА\n\n"
        f"⚽ Загаданный игрок: {player['name']}\n\n"
        "🎮 Чтобы начать снова — /kviz"
    )


# =========================================================
# PLAYER GUESS
# =========================================================

@dp.message()
async def handle_guess(message: Message):
    user_id = message.from_user.id

    # Если это не текст — игнорируем
    if not message.text:
        return

    # Не обрабатываем команды
    if message.text.startswith("/"):
        return

    # Нет активной игры
    if user_id not in games:
        return

    if not await require_subscription(message):
        return

    player = games[user_id]

    answer = message.text.strip().lower()
    correct_answer = player["name"].strip().lower()

    add_player_guess(player["name"])

    if answer == correct_answer:

        games.pop(user_id, None)
        timers.pop(user_id, None)

        add_correct(user_id)

        correct = get_correct(user_id)

        await message.answer(
            "✅ ПРАВИЛЬНО!\n\n"
            f"⚽ Игрок: {player['name']}\n"
            f"🌍 Нация: {player['nation']}\n"
            f"⭐ Рейтинг: {player['rating']}\n"
            f"📍 Позиция: {player['position']}\n\n"
            f"🏆 Твои правильные ответы: {correct}\n\n"
            "🎮 Следующий раунд: /kviz"
        )

    else:

        await message.answer(
            "❌ Неправильно!\n"
            "Попробуй ещё раз 👀"
        )


# =========================================================
# PROFILE
# =========================================================

@dp.message(Command("profile"))
async def profile(message: Message):
    if not await require_subscription(message):
        return

    user_id = message.from_user.id

    register_user(
        user_id,
        message.from_user.username
    )

    correct = get_correct(user_id)

    await message.answer(
        "👤 ТВОЙ ПРОФИЛЬ\n\n"
        f"👤 Пользователь: "
        f"@{message.from_user.username or 'Без имени'}\n\n"
        f"✅ Угадано: {correct}\n"
        f"🏆 Кубок: {get_cup(correct)}"
    )


# =========================================================
# TOP
# =========================================================

@dp.message(Command("top"))
async def top_users(message: Message):
    if not await require_subscription(message):
        return

    CURSOR.execute(
        """
        SELECT username, correct
        FROM users
        ORDER BY correct DESC
        LIMIT 10
        """
    )

    rows = CURSOR.fetchall()

    if not rows:
        await message.answer(
            "🏆 Рейтинг пока пуст."
        )
        return

    text = "🏆 ТОП-10 ИГРОКОВ\n\n"

    for index, row in enumerate(rows, start=1):

        username = row[0] or "Без имени"
        correct = row[1]

        if index == 1:
            medal = "🥇"
        elif index == 2:
            medal = "🥈"
        elif index == 3:
            medal = "🥉"
        else:
            medal = f"{index}."

        text += (
            f"{medal} {username} — "
            f"✅ {correct}\n"
        )

    await message.answer(text)


# =========================================================
# PLAYERS
# =========================================================

@dp.message(Command("players"))
async def players_command(message: Message):
    if not await require_subscription(message):
        return

    sorted_players = sorted(
        PLAYERS,
        key=lambda x: x["rating"],
        reverse=True
    )

    text = "⭐ ТОП-10 ФУТБОЛИСТОВ\n\n"

    for i, player in enumerate(
        sorted_players[:10],
        start=1
    ):
        text += (
            f"{i}. {player['name']} — "
            f"{player['rating']}\n"
        )

    await message.answer(text)


# =========================================================
# HELP
# =========================================================

@dp.message(Command("help"))
async def help_command(message: Message):
    if not await require_subscription(message):
        return

    await message.answer(
        "📖 КОМАНДЫ БОТА\n\n"
        "🎮 /kviz — начать игру\n"
        "🔄 /new — новый раунд\n"
        "🛑 /stop — остановить игру\n"
        "👤 /profile — твой профиль\n"
        "🏆 /top — рейтинг игроков\n"
        "⭐ /players — топ-10 футболистов\n"
        "📖 /help — помощь\n\n"
        "⚽ В игре просто отправляй "
        "имя футболиста сообщением."
    )


# =========================================================
# WEB SERVER FOR RENDER
# =========================================================

from aiohttp import web


async def health(request):
    return web.Response(
        text="BOT IS RUNNING"
    )


async def start_web_server():

    app = web.Application()

    app.router.add_get(
        "/",
        health
    )

    app.router.add_get(
        "/health",
        health
    )

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    runner = web.AppRunner(app)

    await runner.setup()

    site = web.TCPSite(
        runner,
        "0.0.0.0",
        port
    )

    await site.start()

    print(
        f"WEB SERVER STARTED: 0.0.0.0:{port}"
    )


# =========================================================
# MAIN
# =========================================================

async def main():

    print("================================")
    print("BOT STARTED")
    print("PLAYERS:", len(PLAYERS))
    print("ROUND TIME:", ROUND_TIME)
    print("================================")

    await start_web_server()

    await dp.start_polling(bot)


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    asyncio.run(main())
