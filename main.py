import os
import random
import asyncio
import time
import sqlite3
import re

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery


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
# PLAYERS — ТВОИ 110 ИГРОКОВ
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
    {"name": "Энтони Гордон", "nation": "Англия", "rating": 82, "position": "LW"},
    {"name": "Марк Гехи", "nation": "Англия", "rating": 81, "position": "CB"},
    {"name": "Джон Стоунз", "nation": "Англия", "rating": 84, "position": "CB"},
    {"name": "Кайл Уокер", "nation": "Англия", "rating": 83, "position": "RB"},
    {"name": "Пьер-Эмерик Обамеянг", "nation": "Габон", "rating": 81, "position": "ST"},
    {"name": "Сон Хын Мин", "nation": "Южная Корея", "rating": 87, "position": "LW"},
    {"name": "Ким Мин Джэ", "nation": "Южная Корея", "rating": 84, "position": "CB"},
    {"name": "Такефуса Кубо", "nation": "Япония", "rating": 83, "position": "RW"},
    {"name": "Кенан Йылдыз", "nation": "Турция", "rating": 78, "position": "CAM"},
    {"name": "Хакан Чалханоглу", "nation": "Турция", "rating": 86, "position": "CM"},
    {"name": "Николо Барелла", "nation": "Италия", "rating": 87, "position": "CM"},
    {"name": "Федерико Кьеза", "nation": "Италия", "rating": 84, "position": "RW"},
    {"name": "Алессандро Бастони", "nation": "Италия", "rating": 87, "position": "CB"},
    {"name": "Лоренцо Пеллегрини", "nation": "Италия", "rating": 84, "position": "CAM"},
    {"name": "Душан Влахович", "nation": "Сербия", "rating": 84, "position": "ST"},
    {"name": "Александар Митрович", "nation": "Сербия", "rating": 82, "position": "ST"},
    {"name": "Доминик Собослаи", "nation": "Венгрия", "rating": 84, "position": "CAM"},
    {"name": "Матвей Сафонов", "nation": "Россия", "rating": 81, "position": "GK"},
    {"name": "Артём Дзюба", "nation": "Россия", "rating": 72, "position": "ST"},
    {"name": "Франко Мастантуоно", "nation": "Аргентина", "rating": 78, "position": "CAM"},
    {"name": "Эстевао", "nation": "Бразилия", "rating": 79, "position": "RW"},
    {"name": "Эндрик", "nation": "Бразилия", "rating": 77, "position": "ST"},
    {"name": "Уоррен Заир-Эмери", "nation": "Франция", "rating": 81, "position": "CM"},
    {"name": "Брэдли Баркола", "nation": "Франция", "rating": 84, "position": "LW"},
    {"name": "Жоау Невеш", "nation": "Португалия", "rating": 85, "position": "CM"},
    {"name": "Витинья", "nation": "Португалия", "rating": 88, "position": "CM"},
    {"name": "Дезире Дуэ", "nation": "Франция", "rating": 82, "position": "CAM"},
    {"name": "Джованни Ди Лоренцо", "nation": "Италия", "rating": 83, "position": "RB"},
    {"name": "Ромелу Лукаку", "nation": "Бельгия", "rating": 84, "position": "ST"},
    {"name": "Леандро Троссард", "nation": "Бельгия", "rating": 83, "position": "LW"},
    {"name": "Юри Тилеманс", "nation": "Бельгия", "rating": 82, "position": "CM"},
    {"name": "Роберт Левандовски", "nation": "Польша", "rating": 89, "position": "ST"},
    {"name": "Войцех Щенсный", "nation": "Польша", "rating": 84, "position": "GK"},
    {"name": "Майк Меньян", "nation": "Франция", "rating": 87, "position": "GK"},
    {"name": "Жоау Канселу", "nation": "Португалия", "rating": 86, "position": "RB"},
    {"name": "Анхель Ди Мария", "nation": "Аргентина", "rating": 84, "position": "RW"},
    {"name": "Марко Верратти", "nation": "Италия", "rating": 84, "position": "CM"},
    {"name": "Мемфис Депай", "nation": "Нидерланды", "rating": 82, "position": "ST"},
    {"name": "Френки де Йонг", "nation": "Нидерланды", "rating": 87, "position": "CM"},
    {"name": "Вирджил ван Дейк", "nation": "Нидерланды", "rating": 89, "position": "CB"},
    {"name": "Маттейс де Лигт", "nation": "Нидерланды", "rating": 84, "position": "CB"},
    {"name": "Коди Гакпо", "nation": "Нидерланды", "rating": 83, "position": "LW"},
    {"name": "Дензел Думфрис", "nation": "Нидерланды", "rating": 82, "position": "RB"},
    {"name": "Майкл Эдвардс", "nation": "Англия", "rating": 80, "position": "CM"},
    {"name": "Мартин Субименди", "nation": "Испания", "rating": 85, "position": "CDM"},
    {"name": "Микель Оярсабаль", "nation": "Испания", "rating": 83, "position": "LW"},
]


# =========================================================
# GAME DATA
# =========================================================

games = {}
timers = {}


def get_game_key(message: Message):
    # Личная игра
    if message.chat.type == "private":
        return f"user:{message.from_user.id}"

    # Одна общая игра для всей группы
    return f"chat:{message.chat.id}"


# =========================================================
# DATABASE
# =========================================================

DB = sqlite3.connect(
    "quiz.db",
    check_same_thread=False
)

CURSOR = DB.cursor()

CURSOR.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    correct INTEGER DEFAULT 0
)
""")

CURSOR.execute("""
CREATE TABLE IF NOT EXISTS player_guesses (
    player_name TEXT PRIMARY KEY,
    guesses INTEGER DEFAULT 0
)
""")

DB.commit()


def register_user(user_id, username):
    CURSOR.execute(
        """
        INSERT OR IGNORE INTO users
        (user_id, username, correct)
        VALUES (?, ?, 0)
        """,
        (user_id, username or "Без имени")
    )

    CURSOR.execute(
        """
        UPDATE users
        SET username = ?
        WHERE user_id = ?
        """,
        (username or "Без имени", user_id)
    )

    DB.commit()


def get_correct(user_id):
    CURSOR.execute(
        """
        SELECT correct
        FROM users
        WHERE user_id = ?
        """,
        (user_id,)
    )

    result = CURSOR.fetchone()

    return result[0] if result else 0


def add_correct(user_id):
    CURSOR.execute(
        """
        UPDATE users
        SET correct = correct + 1
        WHERE user_id = ?
        """,
        (user_id,)
    )

    DB.commit()


def add_player_guess(player_name):
    CURSOR.execute(
        """
        INSERT OR IGNORE INTO player_guesses
        (player_name, guesses)
        VALUES (?, 0)
        """,
        (player_name,)
    )

    CURSOR.execute(
        """
        UPDATE player_guesses
        SET guesses = guesses + 1
        WHERE player_name = ?
        """,
        (player_name,)
    )

    DB.commit()


# =========================================================
# CUP
# =========================================================

def get_cup(correct):

    if correct >= 100:
        return "🏆 Кубок Легенды"

    if correct >= 50:
        return "🥇 Золотой кубок"

    if correct >= 25:
        return "🥈 Серебряный кубок"

    if correct >= 10:
        return "🥉 Бронзовый кубок"

    return "❌ Кубка пока нет"


# =========================================================
# SUBSCRIPTION
# =========================================================

async def check_subscription(user_id):

    try:
        member = await bot.get_chat_member(
            chat_id=CHANNEL,
            user_id=user_id
        )

        if member.status in (
            "member",
            "administrator",
            "creator"
        ):
            return True

        if (
            member.status == "restricted"
            and getattr(member, "is_member", False)
        ):
            return True

        return False

    except Exception as e:
        print(f"Subscription error: {e}")

        # Если Telegram не даёт проверить подписку,
        # не ломаем команды бота.
        return True


def subscribe_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📢 ПОДПИСАТЬСЯ",
                    url=CHANNEL_URL
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ ПРОВЕРИТЬ ПОДПИСКУ",
                    callback_data="check_sub"
                )
            ]
        ]
    )


async def require_subscription(message):

    subscribed = await check_subscription(
        message.from_user.id
    )

    if not subscribed:

        await message.answer(
            "❌ Чтобы пользоваться ботом, "
            "сначала подпишись на канал!\n\n"
            "📢 @LionelMessiG10AT\n\n"
            "После подписки нажми "
            "«✅ ПРОВЕРИТЬ ПОДПИСКУ».",
            reply_markup=subscribe_keyboard()
        )

        return False

    return True


# =========================================================
# CHECK SUB
# =========================================================

@dp.callback_query(
    lambda callback: callback.data == "check_sub"
)
async def check_sub_callback(callback: CallbackQuery):

    subscribed = await check_subscription(
        callback.from_user.id
    )

    if subscribed:

        register_user(
            callback.from_user.id,
            callback.from_user.username
        )

        await callback.message.edit_text(
            "✅ ПОДПИСКА ПОДТВЕРЖДЕНА!\n\n"
            "🎮 Теперь можешь играть.\n\n"
            "Напиши /kviz"
        )

        await callback.answer()

    else:

        await callback.answer(
            "❌ Ты ещё не подписался на канал!",
            show_alert=True
        )


# =========================================================
# NORMALIZE ANSWER
# =========================================================

def normalize_text(text):

    if not text:
        return ""

    text = text.lower().strip()

    # ё = е
    text = text.replace("ё", "е")

    # Убираем знаки препинания
    text = re.sub(
        r"[^\w\s-]",
        " ",
        text,
        flags=re.UNICODE
    )

    text = text.replace("-", " ")

    # Убираем лишние пробелы
    text = " ".join(text.split())

    return text


def answer_is_correct(answer, player):

    answer = normalize_text(answer)
    full_name = normalize_text(player["name"])

    if not answer:
        return False

    # Полное имя
    if answer == full_name:
        return True

    parts = full_name.split()

    # Например:
    # Винисиус
    # Месси
    # Роналду
    #
    # принимаем только если это имя/фамилия
    # однозначно относится к одному игроку.

    for part in parts:

        if answer != part:
            continue

        matches = 0

        for other in PLAYERS:

            other_parts = normalize_text(
                other["name"]
            ).split()

            if part in other_parts:
                matches += 1

        if matches == 1:
            return True

    return False


# =========================================================
# QUESTION
# =========================================================

def question(player):

    return (
        "⚽ УГАДАЙ ИГРОКА\n\n"
        f"🌍 Нация: {player['nation']}\n"
        f"⭐ Рейтинг: {player['rating']}\n"
        f"⚽ Позиция: {player['position']}\n\n"
        "❓ КТО ЭТО?\n\n"
        "✍️ Просто напиши имя футболиста\n"
        "⏱️ У тебя 5 минут!"
    )


# =========================================================
# TIMER
# =========================================================

async def timer_task(key, chat_id):

    await asyncio.sleep(ROUND_TIME)

    if key not in games:
        return

    start_time = timers.get(key)

    if start_time is None:
        return

    if time.time() - start_time < ROUND_TIME:
        return

    player = games.pop(key, None)
    timers.pop(key, None)

    if player:

        try:

            await bot.send_message(
                chat_id,
                "⏰ ВРЕМЯ ВЫШЛО!\n\n"
                f"⚽ Это был: {player['name']}\n\n"
                "🎮 Новый раунд: /kviz"
            )

        except Exception as e:

            print(
                f"TIMER ERROR: {e}"
            )


# =========================================================
# NEW ROUND
# =========================================================

def new_round(key, chat_id):

    player = random.choice(PLAYERS)

    games[key] = player
    timers[key] = time.time()

    asyncio.create_task(
        timer_task(
            key,
            chat_id
        )
    )

    return player


# =========================================================
# START
# =========================================================

@dp.message(Command("start"))
async def start(message: Message):

    if not await require_subscription(message):
        return

    register_user(
        message.from_user.id,
        message.from_user.username
    )

    await message.answer(
        "👋 ДОБРО ПОЖАЛОВАТЬ!\n\n"
        "⚽ Бот «Отгадай игрока»\n\n"
        "🎮 /kviz — начать игру\n"
        "👤 /profile — мой профиль\n"
        "🏆 /top — рейтинг игроков\n"
        "⭐ /players — топ-10 футболистов\n"
        "🛑 /stop — остановить игру\n"
        "📖 /help — все команды"
    )


# =========================================================
# KVIZ
# =========================================================

@dp.message(Command("kviz"))
async def kviz(message: Message):

    if not await require_subscription(message):
        return

    user_id = message.from_user.id
    key = get_game_key(message)

    register_user(
        user_id,
        message.from_user.username
    )

    games.pop(key, None)
    timers.pop(key, None)

    player = new_round(
        key,
        message.chat.id
    )

    print(
        f"KVIZ STARTED: {player['name']} "
        f"CHAT: {message.chat.id}"
    )

    if message.chat.type == "private":

        await message.answer(
            "🎮 НОВЫЙ РАУНД!\n\n" +
            question(player)
        )

    else:

        await message.answer(
            "🎮 НОВЫЙ РАУНД В ГРУППЕ!\n\n"
            "👥 ОТВЕЧАТЬ МОГУТ ВСЕ!\n\n" +
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
    key = get_game_key(message)

    register_user(
        user_id,
        message.from_user.username
    )

    games.pop(key, None)
    timers.pop(key, None)

    player = new_round(
        key,
        message.chat.id
    )

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

    key = get_game_key(message)

    player = games.pop(
        key,
        None
    )

    timers.pop(
        key,
        None
    )

    if player is None:

        await message.answer(
            "❌ Активной игры нет."
        )

        return

    await message.answer(
        "🛑 ИГРА ОСТАНОВЛЕНА\n\n"
        f"⚽ Загаданный игрок: "
        f"{player['name']}\n\n"
        "🎮 Чтобы начать снова — /kviz"
    )


# =========================================================
# GUESS
# =========================================================

@dp.message()
async def handle_guess(message: Message):

    if not message.text:
        return

    if message.text.startswith("/"):
        return

    key = get_game_key(message)

    # Нет активной игры
    if key not in games:
        return

    player = games[key]

    answer = message.text.strip()

    add_player_guess(
        player["name"]
    )

    # =====================================================
    # CORRECT
    # =====================================================

    if answer_is_correct(
        answer,
        player
    ):

        # Сначала закрываем игру,
        # чтобы два человека одновременно
        # не получили очко.
        games.pop(
            key,
            None
        )

        timers.pop(
            key,
            None
        )

        user_id = message.from_user.id

        register_user(
            user_id,
            message.from_user.username
        )

        add_correct(
            user_id
        )

        correct = get_correct(
            user_id
        )

        username = (
            message.from_user.username
            or message.from_user.full_name
            or "Игрок"
        )

        await message.answer(
            "✅ ПРАВИЛЬНО!\n\n"
            f"👤 Ответил: {username}\n"
            f"⚽ Игрок: {player['name']}\n"
            f"🌍 Нация: {player['nation']}\n"
            f"⭐ Рейтинг: {player['rating']}\n"
            f"📍 Позиция: {player['position']}\n\n"
            f"🏆 Правильных ответов: {correct}\n\n"
            "🎮 Следующий раунд: /kviz"
        )

    # =====================================================
    # WRONG
    # =====================================================

    else:

        await message.answer(
            "❌ Неправильно!\n\n"
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

    correct = get_correct(
        user_id
    )

    await message.answer(
        "👤 ТВОЙ ПРОФИЛЬ\n\n"
        f"👤 @{message.from_user.username or 'Без имени'}\n"
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
        ORDER BY correct DESC, user_id ASC
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

    for index, row in enumerate(
        rows,
        start=1
    ):

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

    await message.answer(
        text
    )


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

    for index, player in enumerate(
        sorted_players[:10],
        start=1
    ):

        text += (
            f"{index}. "
            f"{player['name']} — "
            f"{player['rating']}\n"
        )

    await message.answer(
        text
    )


# =========================================================
# HELP
# =========================================================

@dp.message(Command("help"))
async def help_command(message: Message):

    if not await require_subscription(message):
        return

    await message.answer(
        "📖 КОМАНДЫ\n\n"
        "/start — запуск\n"
        "/kviz — начать игру\n"
        "/new — новый раунд\n"
        "/stop — остановить игру\n"
        "/profile — профиль\n"
        "/top — рейтинг\n"
        "/players — топ футболистов\n"
        "/help — помощь\n\n"
        "👥 В ГРУППЕ:\n"
        "1️⃣ Один человек пишет /kviz\n"
        "2️⃣ Бот загадывает игрока\n"
        "3️⃣ Отвечать могут ВСЕ участники\n"
        "4️⃣ Просто пишите имя футболиста"
    )


# =========================================================
# RENDER WEB SERVER
# =========================================================

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

    runner = web.AppRunner(
        app
    )

    await runner.setup()

    site = web.TCPSite(
        runner,
        "0.0.0.0",
        port
    )

    await site.start()

    print(
        f"WEB SERVER STARTED: "
        f"0.0.0.0:{port}"
    )


# =========================================================
# MAIN
# =========================================================

async def main():

    print(
        "=============================="
    )

    print(
        "BOT STARTED"
    )

    print(
        f"PLAYERS: {len(PLAYERS)}"
    )

    print(
        "=============================="
    )

    await start_web_server()

    await dp.start_polling(
        bot
    )


if __name__ == "__main__":
    asyncio.run(main())
