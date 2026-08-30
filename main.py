# main.py
# 🤖 ИИ-АССИСТЕНТ С ГЕНЕРАЦИЕЙ ФОТО
# ВЕРСИЯ 2.0 — ПОЛНАЯ

import os
import time
import random
import asyncio
import html
import json
import aiohttp
from datetime import datetime, timedelta

import aiosqlite
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

try:
    from keep_alive import keep_alive
    keep_alive()
except Exception:
    pass

# =========================================================
# 🔑 ТОКЕНЫ (ЗАМЕНИ НА СВОИ)
# =========================================================
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

# Для реального ИИ нужен OpenAI API ключ
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")

BOT = Bot(token=TOKEN)
DP = Dispatcher()
DB = "ai_assistant.db"

OWNER = "foqlu"
REQUIRED_CHANNEL = os.getenv("REQUIRED_CHANNEL", "")
CHANNEL_LINK = "https://t.me/+MHTPcaFy2j5lOWMy"

# =========================================================
# НАСТРОЙКИ
# =========================================================
FREE_IMAGES_PER_WEEK = 3
IMAGE_PRICE = 10  # Stars
MAX_HISTORY = 50  # Сохраняем последние 50 сообщений в истории

# =========================================================
# ДОНАТ ПАКИ
# =========================================================
DONATE_PACKS = {
    "pack1": {"stars": 10, "images": 5, "name": "🖼️ 5 фото", "emoji": "🪙"},
    "pack2": {"stars": 25, "images": 15, "name": "🖼️ 15 фото", "emoji": "💰"},
    "pack3": {"stars": 50, "images": 40, "name": "🖼️ 40 фото", "emoji": "💎"},
    "pack4": {"stars": 100, "images": 100, "name": "🖼️ 100 фото", "emoji": "👑"},
    "pack5": {"stars": 250, "images": 300, "name": "🔥 300 фото", "emoji": "🔥"},
    "pack6": {"stars": 500, "images": 800, "name": "💎 800 фото", "emoji": "💎"},
}

# =========================================================
# ПРИВЕТСТВИЯ И ОТВЕТЫ ИИ
# =========================================================
GREETINGS = [
    "Привет! Чем могу помочь? 😊",
    "Здравствуй! Задавай любой вопрос! 🤖",
    "Приветствую! Я здесь, чтобы помочь тебе! 🌟",
    "Салют! Что сегодня интересует? 🔥",
    "Хей! Давай общаться! 💬",
]

FUNNY_RESPONSES = [
    "Хм, интересный вопрос! Дай-ка подумаю... 🤔",
    "Ого, ты меня застал врасплох! Сейчас разберусь! 😅",
    "Вот это вопрос! Обожаю такие! 🧠",
    "Ммм, сложно... Но я попробую! 💪",
]

IMAGE_RESPONSES = [
    "Генерирую фото по твоему запросу! 🎨",
    "Создаю шедевр! Подожди немного... 🖼️",
    "ИИ-художник работает! 🔥",
    "Фото будет готово через секунду! ⏳",
]

# =========================================================
# ИНИЦИАЛИЗАЦИЯ БД
# =========================================================
async def init_db():
    async with aiosqlite.connect(DB) as db:
        # Таблица пользователей
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT DEFAULT '',
            first_name TEXT DEFAULT '',
            last_name TEXT DEFAULT '',
            total_requests INTEGER DEFAULT 0,
            total_images INTEGER DEFAULT 0,
            images_used_week INTEGER DEFAULT 0,
            images_week_date TEXT DEFAULT '',
            extra_images INTEGER DEFAULT 0,
            premium_until INTEGER DEFAULT 0,
            vip_level INTEGER DEFAULT 0,
            banned INTEGER DEFAULT 0,
            created_at INTEGER DEFAULT 0,
            total_donated INTEGER DEFAULT 0,
            last_activity INTEGER DEFAULT 0,
            language TEXT DEFAULT 'ru'
        )
        """)

        # Таблица донатов
        await db.execute("""
        CREATE TABLE IF NOT EXISTS donations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            pack_id TEXT NOT NULL,
            stars INTEGER NOT NULL,
            images INTEGER NOT NULL,
            created_at INTEGER DEFAULT 0
        )
        """)

        # Таблица истории чата
        await db.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at INTEGER DEFAULT 0
        )
        """)

        # Таблица промокодов
        await db.execute("""
        CREATE TABLE IF NOT EXISTS promo_codes (
            code TEXT PRIMARY KEY,
            images INTEGER DEFAULT 0,
            activations INTEGER NOT NULL,
            used INTEGER DEFAULT 0,
            created_at INTEGER DEFAULT 0,
            expires_at INTEGER DEFAULT 0
        )
        """)

        # Таблица использований промокодов
        await db.execute("""
        CREATE TABLE IF NOT EXISTS promo_uses (
            code TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            used_at INTEGER DEFAULT 0,
            PRIMARY KEY (code, user_id)
        )
        """)

        # Таблица постов
        await db.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            creator_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            created_at INTEGER DEFAULT 0,
            sent_count INTEGER DEFAULT 0,
            total_users INTEGER DEFAULT 0
        )
        """)

        # Таблица активных ивентов
        await db.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            multiplier REAL DEFAULT 1,
            starts_at INTEGER DEFAULT 0,
            ends_at INTEGER DEFAULT 0,
            active INTEGER DEFAULT 0
        )
        """)

        # Таблица рефералов
        await db.execute("""
        CREATE TABLE IF NOT EXISTS referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referrer_id INTEGER NOT NULL,
            referred_id INTEGER NOT NULL,
            created_at INTEGER DEFAULT 0,
            reward_claimed INTEGER DEFAULT 0
        )
        """)

        await db.commit()

# =========================================================
# ФУНКЦИИ ПОЛЬЗОВАТЕЛЯ
# =========================================================
async def register_user(user_id, username="", first_name="", last_name=""):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        if await cur.fetchone():
            return
        
        today = datetime.now().strftime("%Y-%m-%d")
        await db.execute("""
            INSERT INTO users (user_id, username, first_name, last_name, images_week_date, created_at, last_activity)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, username, first_name, last_name, today, int(time.time()), int(time.time())))
        await db.commit()

async def get_user(user_id):
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return await cur.fetchone()

async def update_user_activity(user_id):
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET last_activity = ? WHERE user_id = ?", (int(time.time()), user_id))
        await db.commit()

async def get_available_images(user_id):
    user = await get_user(user_id)
    if not user:
        return 0
    
    today = datetime.now().strftime("%Y-%m-%d")
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    # Если неделя обновилась
    if user['images_week_date'] < week_ago:
        user['images_used_week'] = 0
        async with aiosqlite.connect(DB) as db:
            await db.execute("UPDATE users SET images_used_week = 0, images_week_date = ? WHERE user_id = ?",
                           (today, user_id))
            await db.commit()
    
    return FREE_IMAGES_PER_WEEK - user['images_used_week'] + user['extra_images']

async def add_extra_images(user_id, count):
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET extra_images = extra_images + ? WHERE user_id = ?", (count, user_id))
        await db.commit()

async def get_chat_history(user_id, limit=20):
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("""
            SELECT role, content FROM chat_history 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (user_id, limit))
        rows = await cur.fetchall()
        return list(reversed(rows))

async def save_chat_message(user_id, role, content):
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
            INSERT INTO chat_history (user_id, role, content, created_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, role, content, int(time.time())))
        await db.commit()

def is_owner(user):
    return (user.username or "").lower() == OWNER.lower()

# =========================================================
# ПРОВЕРКА ПОДПИСКИ
# =========================================================
async def check_subscription(user_id):
    if not REQUIRED_CHANNEL:
        return True
    try:
        member = await BOT.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status in ("creator", "administrator", "member")
    except:
        return False

def subscribe_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="📢 Подписаться на канал", url=CHANNEL_LINK)
    kb.button(text="✅ Проверить подписку", callback_data="check_sub")
    kb.adjust(1)
    return kb.as_markup()

async def require_subscription(message):
    if is_owner(message.from_user):
        return True
    if not REQUIRED_CHANNEL:
        return True
    if await check_subscription(message.from_user.id):
        return True
    
    kb = subscribe_keyboard()
    await message.answer(
        "🔒 <b>ТРЕБУЕТСЯ ПОДПИСКА</b>\n\n"
        "Для использования бота подпишись на канал:\n"
        f"{CHANNEL_LINK}\n\n"
        "После подписки нажми «Проверить подписку»",
        reply_markup=kb,
        parse_mode="HTML"
    )
    return False

@DP.callback_query(F.data == "check_sub")
async def check_sub_callback(callback: CallbackQuery):
    await callback.answer()
    if await check_subscription(callback.from_user.id):
        await callback.message.edit_text(
            "✅ <b>Подписка подтверждена!</b>\n\n"
            "Теперь ты можешь пользоваться ботом! 🚀",
            reply_markup=main_keyboard(),
            parse_mode="HTML"
        )
    else:
        await callback.message.answer(
            "❌ <b>Подписка не найдена</b>\n\n"
            "Убедись что подписался на канал и нажми кнопку снова.",
            reply_markup=subscribe_keyboard(),
            parse_mode="HTML"
        )

# =========================================================
# КЛАВИАТУРЫ
# =========================================================
def main_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="👤 Профиль", callback_data="profile")
    kb.button(text="💬 Чат с ИИ", callback_data="chat")
    kb.button(text="🖼️ Создать фото", callback_data="generate_image")
    kb.button(text="📰 Новости", callback_data="news")
    kb.button(text="🌤️ Погода", callback_data="weather")
    kb.button(text="💰 Крипто", callback_data="crypto")
    kb.button(text="⭐ Купить фото", callback_data="donate")
    kb.button(text="🎟️ Промокод", callback_data="promo")
    kb.button(text="📊 Статистика", callback_data="stats")
    kb.button(text="🔄 Очистить историю", callback_data="clear_history")
    kb.adjust(2)
    return kb.as_markup()

def donate_keyboard():
    kb = InlineKeyboardBuilder()
    for key, data in DONATE_PACKS.items():
        kb.button(text=f"{data['emoji']} {data['name']} — {data['stars']} ⭐", callback_data=f"donate:{key}")
    kb.button(text="⬅️ Назад", callback_data="menu")
    kb.adjust(1)
    return kb.as_markup()

def admin_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="📊 Статистика", callback_data="admin_stats")
    kb.button(text="📨 Создать пост", callback_data="admin_post")
    kb.button(text="🎟️ Создать промокод", callback_data="admin_promo")
    kb.button(text="🚫 Забанить", callback_data="admin_ban")
    kb.button(text="✅ Разбанить", callback_data="admin_unban")
    kb.button(text="🎉 Ивенты", callback_data="admin_events")
    kb.button(text="⬅️ Назад", callback_data="menu")
    kb.adjust(2)
    return kb.as_markup()

# =========================================================
# КОМАНДА /start
# =========================================================
@DP.message(Command("start"))
async def start_command(message: Message):
    await register_user(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.first_name or "",
        message.from_user.last_name or ""
    )
    
    if not await require_subscription(message):
        return
    
    user = await get_user(message.from_user.id)
    available = await get_available_images(message.from_user.id)
    
    kb = main_keyboard()
    await message.answer(
        f"🤖 <b>ИИ-АССИСТЕНТ</b>\n\n"
        f"Привет, <b>{html.escape(message.from_user.first_name)}</b>!\n\n"
        f"📊 Запросов: <b>{user['total_requests']}</b>\n"
        f"🖼️ Доступно фото: <b>{available}</b>\n"
        f"💰 Цена фото: <b>{IMAGE_PRICE} ⭐</b>\n\n"
        f"💬 <b>Просто напиши мне вопрос!</b>\n"
        f"🖼️ <code>/image описание фото</code>\n\n"
        f"📰 /news — последние новости\n"
        f"🌤️ /weather Москва — погода\n"
        f"💰 /crypto — курсы криптовалют",
        reply_markup=kb,
        parse_mode="HTML"
    )

# =========================================================
# КОМАНДА /help
# =========================================================
@DP.message(Command("help"))
async def help_command(message: Message):
    if not await require_subscription(message):
        return
    
    text = (
        "🤖 <b>ПОМОЩЬ ПО БОТУ</b>\n\n"
        "💬 <b>Чат с ИИ</b>\n"
        "Просто напиши любое сообщение — я отвечу!\n\n"
        "🖼️ <b>Генерация фото</b>\n"
        "<code>/image описание фото</code>\n"
        f"Бесплатно: <b>{FREE_IMAGES_PER_WEEK} фото</b> в неделю\n"
        f"Платно: <b>{IMAGE_PRICE} ⭐</b> за фото\n\n"
        "📰 <b>Новости</b>\n"
        "/news — последние новости\n\n"
        "🌤️ <b>Погода</b>\n"
        "/weather Москва — погода в городе\n\n"
        "💰 <b>Крипто</b>\n"
        "/crypto — курсы криптовалют\n\n"
        "⭐ <b>Купить фото</b>\n"
        "/donate — купить пак фото за Stars\n\n"
        "🎟️ <b>Промокод</b>\n"
        "/promo КОД — активировать промокод"
    )
    
    await message.answer(text, parse_mode="HTML", reply_markup=main_keyboard())

# =========================================================
# ПРОФИЛЬ
# =========================================================
@DP.callback_query(F.data == "profile")
async def profile_callback(callback: CallbackQuery):
    await callback.answer()
    user = await get_user(callback.from_user.id)
    available = await get_available_images(callback.from_user.id)
    
    await callback.message.edit_text(
        f"👤 <b>ПРОФИЛЬ</b>\n\n"
        f"👤 Имя: {html.escape(user['first_name'])}\n"
        f"📊 Всего запросов: <b>{user['total_requests']}</b>\n"
        f"🖼️ Сгенерировано фото: <b>{user['total_images']}</b>\n"
        f"🖼️ Доступно фото: <b>{available}</b>\n"
        f"🖼️ Использовано за неделю: <b>{user['images_used_week']}/{FREE_IMAGES_PER_WEEK}</b>\n"
        f"⭐ Потрачено Stars: <b>{user['total_donated']}</b>\n"
        f"📅 Зарегистрирован: {datetime.fromtimestamp(user['created_at']).strftime('%d.%m.%Y')}",
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )

# =========================================================
# ЧАТ С ИИ
# =========================================================
@DP.callback_query(F.data == "chat")
async def chat_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "💬 <b>ЧАТ С ИИ</b>\n\n"
        "Просто напиши мне любое сообщение!\n\n"
        "Я отвечу на любой вопрос, помогу с идеями,\n"
        "объясню сложные вещи простым языком.\n\n"
        "🧠 <b>Что я умею:</b>\n"
        "• Отвечать на вопросы\n"
        "• Помогать с идеями\n"
        "• Объяснять сложное\n"
        "• Переводить тексты\n"
        "• Писать тексты\n\n"
        "Напиши что-нибудь! 👇",
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )

# =========================================================
# ОБРАБОТКА СООБЩЕНИЙ (ЧАТ С ИИ)
# =========================================================
@DP.message(F.text & ~F.text.startswith('/'))
async def handle_chat(message: Message):
    if not await require_subscription(message):
        return
    
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer("❌ Напиши /start")
        return
    
    await update_user_activity(message.from_user.id)
    
    # Сохраняем сообщение пользователя
    await save_chat_message(message.from_user.id, "user", message.text)
    
    # Обновляем статистику
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET total_requests = total_requests + 1 WHERE user_id = ?", 
                       (message.from_user.id,))
        await db.commit()
    
    # Показываем "печатает"
    await BOT.send_chat_action(message.chat.id, "typing")
    
    # Получаем историю для контекста
    history = await get_chat_history(message.from_user.id, 20)
    
    # Эмуляция ответа ИИ (для реального нужно подключить OpenAI)
    await asyncio.sleep(random.uniform(1, 2.5))
    
    # Генерируем ответ
    responses = [
        f"🤔 Хм, интересный вопрос!\n\nЯ думаю, что ответ на твой вопрос: «{message.text}» — это очень важно. Давай разберёмся подробнее! 📚\n\nЕсли хочешь, я могу помочь тебе с этим! 😊",
        
        f"🧠 Отличный вопрос!\n\n«{message.text}» — это тема, о которой можно говорить долго. Я считаю, что главное здесь — это понимание и практика. 💡\n\nЧто именно тебя интересует?",
        
        f"💡 Класс!\n\n«{message.text}» — это как раз то, о чём я люблю думать! 🤔\n\nЕсли хочешь, я могу дать тебе несколько советов по этой теме! 🚀",
        
        f"🌟 Супер!\n\n«{message.text}» — это очень актуально. Я думаю, что каждый должен разобраться в этом. 💪\n\nДавай обсудим это подробнее! 💬",
        
        f"🔥 Огонь!\n\n«{message.text}» — это то, что я обожаю! 😎\n\nЕсли тебе нужно больше информации — я здесь! 🤖",
        
        f"📚 Очень интересно!\n\n«{message.text}» — это тема, которую я изучал. Думаю, что здесь важно понимать основы. 🧠\n\nЧто именно ты хочешь узнать?",
        
        f"💎 Глубокий вопрос!\n\n«{message.text}» — это то, что заставляет задуматься. Давай разберём это вместе! 🤝\n\nЯ готов помочь тебе разобраться!",
    ]
    
    response = random.choice(responses)
    
    # Сохраняем ответ ИИ
    await save_chat_message(message.from_user.id, "assistant", response)
    
    # Отправляем ответ
    kb = InlineKeyboardBuilder()
    kb.button(text="💬 Продолжить диалог", callback_data="chat")
    kb.button(text="🔄 Новый вопрос", callback_data="chat")
    kb.button(text="⬅️ Меню", callback_data="menu")
    kb.adjust(1)
    
    await message.answer(
        response,
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )

# =========================================================
# ГЕНЕРАЦИЯ ФОТО
# =========================================================
@DP.message(Command("image"))
async def image_command(message: Message):
    if not await require_subscription(message):
        return
    
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        kb = InlineKeyboardBuilder()
        kb.button(text="🖼️ Создать фото", callback_data="generate_image")
        kb.button(text="⬅️ Назад", callback_data="menu")
        kb.adjust(1)
        
        await message.answer(
            "🖼️ <b>ГЕНЕРАЦИЯ ФОТО</b>\n\n"
            "<code>/image описание фото</code>\n\n"
            "📝 <b>Примеры:</b>\n"
            "/image красивый закат на море\n"
            "/image робот читает книгу\n"
            "/image космический корабль\n\n"
            f"💰 Цена: <b>{IMAGE_PRICE} ⭐</b>\n"
            f"🎁 Бесплатно: <b>{FREE_IMAGES_PER_WEEK} фото</b> в неделю\n\n"
            "Используй /donate чтобы купить фото!",
            reply_markup=kb.as_markup(),
            parse_mode="HTML"
        )
        return
    
    prompt = parts[1]
    user = await get_user(message.from_user.id)
    available = await get_available_images(message.from_user.id)
    
    if available <= 0:
        kb = InlineKeyboardBuilder()
        kb.button(text="⭐ Купить фото", callback_data="donate")
        kb.button(text="⬅️ Назад", callback_data="menu")
        kb.adjust(1)
        
        await message.answer(
            f"❌ <b>НЕТ ДОСТУПНЫХ ФОТО</b>\n\n"
            f"Бесплатный лимит: <b>{FREE_IMAGES_PER_WEEK} фото</b> в неделю\n"
            f"Цена: <b>{IMAGE_PRICE} ⭐</b> за фото\n\n"
            f"Купи пак фото за Stars!",
            reply_markup=kb.as_markup(),
            parse_mode="HTML"
        )
        return
    
    # Проверяем, бесплатное или платное
    is_free = user['images_used_week'] < FREE_IMAGES_PER_WEEK
    
    if is_free:
        # Бесплатное фото
        await BOT.send_chat_action(message.chat.id, "upload_photo")
        await asyncio.sleep(2)
        
        async with aiosqlite.connect(DB) as db:
            await db.execute("UPDATE users SET images_used_week = images_used_week + 1, total_images = total_images + 1 WHERE user_id = ?",
                           (message.from_user.id,))
            await db.commit()
        
        await message.answer_photo(
            photo="https://i.pravatar.cc/800?img=" + str(random.randint(1, 70)),
            caption=f"🖼️ <b>ФОТО ГОТОВО!</b>\n\n"
                   f"📝 Запрос: <i>{html.escape(prompt)}</i>\n"
                   f"🎁 Бесплатное (осталось: {available-1})",
            parse_mode="HTML"
        )
        
    else:
        # Платное фото (через Stars)
        await BOT.send_invoice(
            chat_id=message.chat.id,
            title="🖼️ Генерация фото",
            description=f"Создам фото по запросу: {prompt[:50]}...",
            payload=f"image:{prompt}",
            currency="XTR",
            prices=[LabeledPrice(label="Генерация фото", amount=IMAGE_PRICE)]
        )

@DP.callback_query(F.data == "generate_image")
async def generate_image_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "🖼️ <b>ГЕНЕРАЦИЯ ФОТО</b>\n\n"
        "Введи команду:\n"
        "<code>/image описание фото</code>\n\n"
        "Пример: <code>/image красивый закат</code>",
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )

# =========================================================
# НОВОСТИ
# =========================================================
@DP.callback_query(F.data == "news")
async def news_callback(callback: CallbackQuery):
    await callback.answer()
    
    # Эмуляция новостей (для реальных нужно подключить API)
    await BOT.send_chat_action(callback.message.chat.id, "typing")
    await asyncio.sleep(1)
    
    # Генерируем фейковые новости (для демонстрации)
    news_items = [
        {"title": "📰 Курс Bitcoin пробил $70,000", "desc": "Криптовалюта продолжает расти на фоне новостей...", "source": "CoinDesk"},
        {"title": "🚀 SpaceX запускает новый спутник", "desc": "Компания Илона Маска продолжает расширение...", "source": "SpaceNews"},
        {"title": "🤖 ИИ научился генерировать видео", "desc": "Новая модель OpenAI поражает реалистичностью...", "source": "TechCrunch"},
        {"title": "💎 Telegram запускает новые функции", "desc": "Платформа обновляет возможности для ботов...", "source": "Telegram"},
        {"title": "📱 Apple представляет iPhone 17", "desc": "Новый смартфон получил ИИ-процессор...", "source": "AppleInsider"},
    ]
    
    text = "📰 <b>ПОСЛЕДНИЕ НОВОСТИ</b>\n\n"
    for i, item in enumerate(news_items, 1):
        text += f"{i}. <b>{item['title']}</b>\n"
        text += f"   {item['desc'][:100]}...\n"
        text += f"   📍 {item['source']}\n\n"
    
    kb = InlineKeyboardBuilder()
    kb.button(text="🔄 Обновить", callback_data="news")
    kb.button(text="⬅️ Назад", callback_data="menu")
    kb.adjust(2)
    
    await callback.message.edit_text(
        text,
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )

# =========================================================
# ПОГОДА
# =========================================================
@DP.message(Command("weather"))
async def weather_command(message: Message):
    if not await require_subscription(message):
        return
    
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "🌤️ <b>ПОГОДА</b>\n\n"
            "<code>/weather ГОРОД</code>\n\n"
            "Пример: <code>/weather Москва</code>",
            parse_mode="HTML"
        )
        return
    
    city = parts[1]
    
    await BOT.send_chat_action(message.chat.id, "typing")
    await asyncio.sleep(1.5)
    
    # Эмуляция погоды (для реальной нужен API)
    temp = random.randint(-15, 35)
    feels_like = temp + random.randint(-3, 3)
    conditions = ["Ясно ☀️", "Облачно ☁️", "Дождь 🌧️", "Снег ❄️", "Туман 🌫️", "Ветер 🌬️"]
    condition = random.choice(conditions)
    humidity = random.randint(30, 90)
    wind = random.randint(0, 25)
    
    await message.answer(
        f"🌤️ <b>ПОГОДА В {city.upper()}</b>\n\n"
        f"🌡️ Температура: <b>{temp}°C</b> (ощущается как {feels_like}°C)\n"
        f"☁️ {condition}\n"
        f"💧 Влажность: <b>{humidity}%</b>\n"
        f"💨 Ветер: <b>{wind} м/с</b>\n\n"
        f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}",
        parse_mode="HTML"
    )

@DP.callback_query(F.data == "weather")
async def weather_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "🌤️ <b>ПОГОДА</b>\n\n"
        "Введи команду:\n"
        "<code>/weather ГОРОД</code>\n\n"
        "Пример: <code>/weather Москва</code>",
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )

# =========================================================
# КРИПТОВАЛЮТЫ
# =========================================================
@DP.callback_query(F.data == "crypto")
async def crypto_callback(callback: CallbackQuery):
    await callback.answer()
    
    await BOT.send_chat_action(callback.message.chat.id, "typing")
    await asyncio.sleep(1)
    
    # Эмуляция курсов криптовалют
    crypto_data = [
        {"name": "Bitcoin", "symbol": "BTC", "price": random.randint(68000, 72000), "change": random.uniform(-5, 5)},
        {"name": "Ethereum", "symbol": "ETH", "price": random.randint(3400, 3600), "change": random.uniform(-5, 5)},
        {"name": "Solana", "symbol": "SOL", "price": random.randint(170, 190), "change": random.uniform(-5, 5)},
        {"name": "Dogecoin", "symbol": "DOGE", "price": random.randint(14, 16) / 100, "change": random.uniform(-5, 5)},
        {"name": "Shiba Inu", "symbol": "SHIB", "price": random.randint(2, 3) / 100000, "change": random.uniform(-5, 5)},
    ]
    
    text = "💰 <b>КУРСЫ КРИПТОВАЛЮТ</b>\n\n"
    for c in crypto_data:
        emoji = "📈" if c['change'] >= 0 else "📉"
        sign = "+" if c['change'] >= 0 else ""
        price_str = f"${c['price']:,}" if c['price'] > 1 else f"${c['price']:.5f}"
        text += f"{emoji} <b>{c['name']}</b> ({c['symbol']})\n"
        text += f"   💰 {price_str} | {sign}{c['change']:.2f}%\n\n"
    
    text += f"🔄 Обновлено: {datetime.now().strftime('%H:%M:%S')}"
    
    kb = InlineKeyboardBuilder()
    kb.button(text="🔄 Обновить", callback_data="crypto")
    kb.button(text="⬅️ Назад", callback_data="menu")
    kb.adjust(2)
    
    await callback.message.edit_text(
        text,
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )

# =========================================================
# ДОНАТ
# =========================================================
@DP.callback_query(F.data == "donate")
async def donate_callback(callback: CallbackQuery):
    await callback.answer()
    user = await get_user(callback.from_user.id)
    available = await get_available_images(callback.from_user.id)
    
    text = (
        f"⭐ <b>КУПИТЬ ФОТО</b>\n\n"
        f"🖼️ Доступно фото: <b>{available}</b>\n"
        f"💰 Цена: <b>{IMAGE_PRICE} ⭐</b> за фото\n\n"
        f"<b>Выбери пак:</b>"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=donate_keyboard(),
        parse_mode="HTML"
    )

@DP.callback_query(F.data.startswith("donate:"))
async def donate_pack_callback(callback: CallbackQuery):
    await callback.answer()
    key = callback.data.split(":")[1]
    pack = DONATE_PACKS.get(key)
    if not pack:
        return
    
    await BOT.send_invoice(
        chat_id=callback.from_user.id,
        title=pack['name'],
        description=f"{pack['images']} фото для ИИ генерации",
        payload=f"donate:{key}",
        currency="XTR",
        prices=[LabeledPrice(label=pack['name'], amount=pack['stars'])]
    )

# =========================================================
# ПРОМОКОДЫ
# =========================================================
@DP.callback_query(F.data == "promo")
async def promo_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "🎟️ <b>ПРОМОКОД</b>\n\n"
        "Введи промокод командой:\n"
        "<code>/promo КОД</code>\n\n"
        "Промокод даёт бесплатные фото! 🖼️\n\n"
        "Следи за новостями, чтобы не пропустить новые промокоды!",
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )

@DP.message(Command("promo"))
async def promo_command(message: Message):
    if not await require_subscription(message):
        return
    
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer(
            "🎟️ <b>ПРОМОКОД</b>\n\n"
            "<code>/promo КОД</code>\n\n"
            "Пример: <code>/promo FREE10</code>",
            parse_mode="HTML"
        )
        return
    
    code = parts[1].upper()
    
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM promo_codes WHERE code = ?", (code,))
        promo = await cur.fetchone()
        
        if not promo:
            await message.answer("❌ <b>Промокод не найден!</b>\n\nПроверь правильность кода.", parse_mode="HTML")
            return
        
        # Проверяем срок действия
        if promo['expires_at'] > 0 and promo['expires_at'] < int(time.time()):
            await message.answer("❌ <b>Промокод истёк!</b>", parse_mode="HTML")
            return
        
        cur2 = await db.execute("SELECT 1 FROM promo_uses WHERE code = ? AND user_id = ?", (code, message.from_user.id))
        if await cur2.fetchone():
            await message.answer("❌ <b>Ты уже использовал этот промокод!</b>", parse_mode="HTML")
            return
        
        if promo['used'] >= promo['activations']:
            await message.answer("❌ <b>Лимит активаций исчерпан!</b>", parse_mode="HTML")
            return
        
        await db.execute("INSERT INTO promo_uses (code, user_id, used_at) VALUES (?, ?, ?)",
                       (code, message.from_user.id, int(time.time())))
        await db.execute("UPDATE promo_codes SET used = used + 1 WHERE code = ?", (code,))
        await db.execute("UPDATE users SET extra_images = extra_images + ? WHERE user_id = ?",
                       (promo['images'], message.from_user.id))
        await db.commit()
    
    await message.answer(
        f"🎉 <b>ПРОМОКОД АКТИВИРОВАН!</b>\n\n"
        f"🖼️ Получено фото: <b>+{promo['images']}</b>\n\n"
        f"Теперь у тебя больше фото для генерации! 🚀",
        parse_mode="HTML"
    )

# =========================================================
# СТАТИСТИКА
# =========================================================
@DP.callback_query(F.data == "stats")
async def stats_callback(callback: CallbackQuery):
    await callback.answer()
    user = await get_user(callback.from_user.id)
    available = await get_available_images(callback.from_user.id)
    
    text = (
        f"📊 <b>ТВОЯ СТАТИСТИКА</b>\n\n"
        f"💬 Всего запросов: <b>{user['total_requests']}</b>\n"
        f"🖼️ Сгенерировано фото: <b>{user['total_images']}</b>\n"
        f"🖼️ Доступно фото: <b>{available}</b>\n"
        f"⭐ Потрачено Stars: <b>{user['total_donated']}</b>\n"
        f"📅 Последняя активность: {datetime.fromtimestamp(user['last_activity']).strftime('%d.%m.%Y %H:%M')}"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )

# =========================================================
# ОЧИСТКА ИСТОРИИ
# =========================================================
@DP.callback_query(F.data == "clear_history")
async def clear_history_callback(callback: CallbackQuery):
    await callback.answer()
    
    async with aiosqlite.connect(DB) as db:
        await db.execute("DELETE FROM chat_history WHERE user_id = ?", (callback.from_user.id,))
        await db.commit()
    
    await callback.message.edit_text(
        "✅ <b>История чата очищена!</b>\n\n"
        "Теперь ИИ не будет помнить предыдущие сообщения.",
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )

# =========================================================
# АДМИНКА
# =========================================================
@DP.message(Command("admin"))
async def admin_command(message: Message):
    if not is_owner(message.from_user):
        await message.answer("❌ Только для владельца!")
        return
    
    await message.answer(
        "👑 <b>АДМИН-ПАНЕЛЬ</b>\n\n"
        "Выбери действие:",
        reply_markup=admin_keyboard(),
        parse_mode="HTML"
    )

@DP.callback_query(F.data == "admin_stats")
async def admin_stats_callback(callback: CallbackQuery):
    await callback.answer()
    if not is_owner(callback.from_user):
        return
    
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT COUNT(*) FROM users")
        users = (await cur.fetchone())[0]
        
        cur = await db.execute("SELECT SUM(total_requests) FROM users")
        total_requests = (await cur.fetchone())[0] or 0
        
        cur = await db.execute("SELECT SUM(total_images) FROM users")
        total_images = (await cur.fetchone())[0] or 0
        
        cur = await db.execute("SELECT SUM(total_donated) FROM users")
        total_donated = (await cur.fetchone())[0] or 0
        
        cur = await db.execute("SELECT COUNT(*) FROM users WHERE banned = 1")
        banned = (await cur.fetchone())[0]
    
    await callback.message.edit_text(
        f"📊 <b>ОБЩАЯ СТАТИСТИКА</b>\n\n"
        f"👥 Пользователей: <b>{users}</b>\n"
        f"🚫 Забанено: <b>{banned}</b>\n"
        f"💬 Всего запросов: <b>{total_requests}</b>\n"
        f"🖼️ Всего фото: <b>{total_images}</b>\n"
        f"⭐ Получено Stars: <b>{total_donated}</b>",
        reply_markup=admin_keyboard(),
        parse_mode="HTML"
    )

@DP.callback_query(F.data == "admin_post")
async def admin_post_callback(callback: CallbackQuery):
    await callback.answer()
    if not is_owner(callback.from_user):
        return
    
    await callback.message.edit_text(
        "📨 <b>СОЗДАНИЕ ПОСТА</b>\n\n"
        "Введи команду:\n"
        "<code>/post ТЕКСТ ПОСТА</code>\n\n"
        "Пост будет отправлен всем пользователям бота.\n\n"
        "Пример:\n"
        "<code>/post Привет всем! Сегодня бесплатные фото для всех! 🔥</code>",
        reply_markup=admin_keyboard(),
        parse_mode="HTML"
    )

@DP.message(Command("post"))
async def post_command(message: Message):
    if not is_owner(message.from_user):
        await message.answer("❌ Только для владельца!")
        return
    
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "📨 <b>СОЗДАНИЕ ПОСТА</b>\n\n"
            "<code>/post ТЕКСТ ПОСТА</code>",
            parse_mode="HTML"
        )
        return
    
    text = parts[1]
    
    # Сохраняем пост
    async with aiosqlite.connect(DB) as db:
        await db.execute("INSERT INTO posts (creator_id, text, created_at) VALUES (?, ?, ?)",
                       (message.from_user.id, text, int(time.time())))
        await db.commit()
    
    # Получаем всех пользователей
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT user_id FROM users WHERE banned = 0")
        users = await cur.fetchall()
    
    sent = 0
    for row in users:
        try:
            await BOT.send_message(
                row[0],
                f"📢 <b>ОБЪЯВЛЕНИЕ</b>\n\n{text}\n\n---\n🤖 <i>ИИ-Ассистент</i>",
                parse_mode="HTML"
            )
            sent += 1
            await asyncio.sleep(0.05)
        except:
            pass
    
    await message.answer(
        f"✅ <b>ПОСТ ОТПРАВЛЕН!</b>\n\n"
        f"📨 Отправлено пользователям: <b>{sent}</b>",
        parse_mode="HTML"
    )

@DP.callback_query(F.data == "admin_promo")
async def admin_promo_callback(callback: CallbackQuery):
    await callback.answer()
    if not is_owner(callback.from_user):
        return
    
    await callback.message.edit_text(
        "🎟️ <b>СОЗДАНИЕ ПРОМОКОДА</b>\n\n"
        "Введи команду:\n"
        "<code>/createpromo КОД ФОТО ЛИМИТ</code>\n\n"
        "Пример:\n"
        "<code>/createpromo FREE10 10 100</code>\n\n"
        "Создаст промокод FREE10 на 10 фото, 100 активаций.",
        reply_markup=admin_keyboard(),
        parse_mode="HTML"
    )

@DP.message(Command("createpromo"))
async def create_promo_command(message: Message):
    if not is_owner(message.from_user):
        await message.answer("❌ Только для владельца!")
        return
    
    parts = message.text.split()
    if len(parts) != 4:
        await message.answer(
            "🎟️ <b>СОЗДАНИЕ ПРОМОКОДА</b>\n\n"
            "<code>/createpromo КОД ФОТО ЛИМИТ</code>\n"
            "Пример: <code>/createpromo FREE10 10 100</code>",
            parse_mode="HTML"
        )
        return
    
    code = parts[1].upper()
    try:
        images = int(parts[2])
        limit = int(parts[3])
    except:
        await message.answer("❌ Неверные данные!", parse_mode="HTML")
        return
    
    # Срок действия: 30 дней
    expires_at = int(time.time()) + 30 * 24 * 60 * 60
    
    async with aiosqlite.connect(DB) as db:
        try:
            await db.execute("""
                INSERT INTO promo_codes (code, images, activations, used, created_at, expires_at)
                VALUES (?, ?, ?, 0, ?, ?)
            """, (code, images, limit, int(time.time()), expires_at))
            await db.commit()
        except:
            await message.answer("❌ <b>Промокод уже существует!</b>", parse_mode="HTML")
            return
    
    await message.answer(
        f"✅ <b>ПРОМОКОД СОЗДАН!</b>\n\n"
        f"🎟️ Код: <code>{code}</code>\n"
        f"🖼️ Фото: <b>{images}</b>\n"
        f"👥 Активаций: <b>{limit}</b>\n"
        f"⏳ Действует до: {datetime.fromtimestamp(expires_at).strftime('%d.%m.%Y')}",
        parse_mode="HTML"
    )

@DP.callback_query(F.data == "admin_ban")
async def admin_ban_callback(callback: CallbackQuery):
    await callback.answer()
    if not is_owner(callback.from_user):
        return
    
    await callback.message.edit_text(
        "🚫 <b>БАН ПОЛЬЗОВАТЕЛЯ</b>\n\n"
        "Введи команду:\n"
        "<code>/ban USER_ID</code>\n\n"
        "Пример: <code>/ban 123456789</code>",
        reply_markup=admin_keyboard(),
        parse_mode="HTML"
    )

@DP.message(Command("ban"))
async def ban_command(message: Message):
    if not is_owner(message.from_user):
        return
    
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("🚫 <code>/ban USER_ID</code>", parse_mode="HTML")
        return
    
    try:
        user_id = int(parts[1])
    except:
        await message.answer("❌ Неверный ID!", parse_mode="HTML")
        return
    
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET banned = 1 WHERE user_id = ?", (user_id,))
        await db.commit()
    
    await message.answer(f"🚫 <b>Пользователь <code>{user_id}</code> забанен!</b>", parse_mode="HTML")

@DP.callback_query(F.data == "admin_unban")
async def admin_unban_callback(callback: CallbackQuery):
    await callback.answer()
    if not is_owner(callback.from_user):
        return
    
    await callback.message.edit_text(
        "✅ <b>РАЗБАН ПОЛЬЗОВАТЕЛЯ</b>\n\n"
        "Введи команду:\n"
        "<code>/unban USER_ID</code>\n\n"
        "Пример: <code>/unban 123456789</code>",
        reply_markup=admin_keyboard(),
        parse_mode="HTML"
    )

@DP.message(Command("unban"))
async def unban_command(message: Message):
    if not is_owner(message.from_user):
        return
    
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("✅ <code>/unban USER_ID</code>", parse_mode="HTML")
        return
    
    try:
        user_id = int(parts[1])
    except:
        await message.answer("❌ Неверный ID!", parse_mode="HTML")
        return
    
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET banned = 0 WHERE user_id = ?", (user_id,))
        await db.commit()
    
    await message.answer(f"✅ <b>Пользователь <code>{user_id}</code> разбанен!</b>", parse_mode="HTML")

# =========================================================
# МЕНЮ
# =========================================================
@DP.callback_query(F.data == "menu")
async def menu_callback(callback: CallbackQuery):
    await callback.answer()
    user = await get_user(callback.from_user.id)
    available = await get_available_images(callback.from_user.id)
    
    text = (
        f"🤖 <b>ИИ-АССИСТЕНТ</b>\n\n"
        f"💰 Баланс: <b>{available} фото</b>\n"
        f"⭐ Уровень: <b>FREE</b>\n\n"
        "Выбери действие:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )

# =========================================================
# ОБРАБОТКА ПЛАТЕЖЕЙ
# =========================================================
@DP.pre_checkout_query()
async def pre_checkout_query(query: PreCheckoutQuery):
    await query.answer(ok=True)

@DP.message(F.successful_payment)
async def successful_payment(message: Message):
    payload = message.successful_payment.invoice_payload
    
    if payload.startswith("image:"):
        prompt = payload.split(":", 1)[1]
        
        await BOT.send_chat_action(message.chat.id, "upload_photo")
        await asyncio.sleep(2)
        
        await message.answer_photo(
            photo="https://i.pravatar.cc/800?img=" + str(random.randint(1, 70)),
            caption=f"🖼️ <b>ФОТО ГОТОВО!</b>\n\n"
                   f"📝 Запрос: <i>{html.escape(prompt)}</i>\n"
                   f"⭐ Оплачено: <b>{IMAGE_PRICE} ⭐</b>",
            parse_mode="HTML"
        )
        
        # Обновляем статистику
        async with aiosqlite.connect(DB) as db:
            await db.execute("UPDATE users SET total_images = total_images + 1 WHERE user_id = ?", (message.from_user.id,))
            await db.commit()
    
    elif payload.startswith("donate:"):
        key = payload.split(":")[1]
        pack = DONATE_PACKS.get(key)
        if pack:
            await add_extra_images(message.from_user.id, pack['images'])
            
            async with aiosqlite.connect(DB) as db:
                await db.execute("UPDATE users SET total_donated = total_donated + ? WHERE user_id = ?",
                               (pack['stars'], message.from_user.id))
                await db.execute("""
                    INSERT INTO donations (user_id, pack_id, stars, images, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (message.from_user.id, key, pack['stars'], pack['images'], int(time.time())))
                await db.commit()
            
            await message.answer(
                f"✅ <b>ПОКУПКА УСПЕШНА!</b>\n\n"
                f"📦 Пак: {pack['name']}\n"
                f"🖼️ Фото: <b>+{pack['images']}</b>\n"
                f"⭐ Потрачено: <b>{pack['stars']}</b>\n\n"
                f"Теперь у тебя больше фото для генерации! 🚀",
                parse_mode="HTML"
            )

# =========================================================
# ЗАПУСК
# =========================================================
async def main():
    await init_db()
    print("=" * 70)
    print("🤖 ИИ-АССИСТЕНТ + ГЕНЕРАЦИЯ ФОТО v2.0")
    print("=" * 70)
    print(f"👑 OWNER: @{OWNER}")
    print(f"📢 КАНАЛ: {CHANNEL_LINK}")
    print(f"🖼️ БЕСПЛАТНЫХ ФОТО: {FREE_IMAGES_PER_WEEK} в неделю")
    print(f"💰 ЦЕНА ФОТО: {IMAGE_PRICE} ⭐")
    print("=" * 70)
    print("Бот запущен и готов к работе! 🚀")
    print("=" * 70)
    await DP.start_polling(BOT)

if __name__ == "__main__":
    asyncio.run(main())
