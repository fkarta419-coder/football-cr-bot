import os
import random
import asyncio
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message


# =========================
# TOKEN
# =========================

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN не найден")


# =========================
# WEB SERVER ДЛЯ RENDER
# =========================

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

    def log_message(self, format, *args):
        return


def run_web():
    port = int(os.getenv("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()


# =========================
# TELEGRAM
# =========================

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
# ИГРЫ
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

    if user_id
