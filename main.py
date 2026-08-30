# main.py
# 🤖 ИИ-АССИСТЕНТ + ГЕНЕРАЦИЯ ФОТО
# Бесплатные запросы всегда, платные фото

import os
import time
import random
import asyncio
import html
import json
import aiohttp
from datetime import datetime, timedelta

import aiosqlite
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

try:
    from keep_alive import keep_alive
    keep_alive()
except Exception:
    pass

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

# Для ИИ нужен API ключ OpenAI (для фото тоже)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
# Для новостей нужен API ключ NewsAPI
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
# Для погоды нужен API ключ OpenWeather
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
FREE_IMAGES_PER_WEEK = 3  # Бесплатных фото в неделю
IMAGE_PRICE = 10  # Цена одного фото в Stars

# =========================================================
# ДОНАТЫ ЗА STARS
# =========================================================
DONATE_PACKS = {
    "pack1": {"stars": 10, "images": 5, "name": "🖼️ 5 фото"},
    "pack2": {"stars": 25, "images": 15, "name": "🖼️ 15 фото"},
    "pack3": {"stars": 50, "images": 40, "name": "🖼️ 40 фото"},
    "pack4": {"stars": 100, "images": 100, "name": "🖼️ 100 фото"},
    "pack5": {"stars": 250, "images": 300, "name": "🔥 300 фото"},
    "pack6": {"stars": 500, "images": 800, "name": "💎 800 фото"},
}

# =========================================================
# ИНИЦИАЛИЗАЦИЯ БД
# =========================================================
async def init_db():
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT DEFAULT '',
            first_name TEXT DEFAULT '',
            total_requests INTEGER DEFAULT 0,
            images_used_week INTEGER DEFAULT 0,
            images_week_date TEXT DEFAULT '',
            extra_images INTEGER DEFAULT 0,
            premium_until INTEGER DEFAULT 0,
            banned INTEGER DEFAULT 0,
            created_at INTEGER DEFAULT 0,
            total_donated INTEGER DEFAULT 0
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS donations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            pack_id TEXT NOT NULL,
            stars INTEGER NOT NULL,
            created_at INTEGER DEFAULT 0
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at INTEGER DEFAULT 0
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS promo_codes (
            code TEXT PRIMARY KEY,
            images INTEGER DEFAULT 0,
            activations INTEGER NOT NULL,
            used INTEGER DEFAULT 0,
            created_at INTEGER DEFAULT 0
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS promo_uses (
            code TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            PRIMARY KEY (code, user_id)
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            creator_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            created_at INTEGER DEFAULT 0,
            sent_count INTEGER DEFAULT 0
        )
        """)

        await db.commit()

# =========================================================
# ФУНКЦИИ
# =========================================================
async def register_user(user_id, username="", first_name=""):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        if await cur.fetchone():
            return
        
        today = datetime.now().strftime("%Y-%m-%d")
        await db.execute("""
            INSERT INTO users (user_id, username, first_name, images_week_date, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, username, first_name, today, int(time.time())))
        await db.commit()

async def get_user(user_id):
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return await cur.fetchone()

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

def is_owner(user):
    return (user.username or "").lower() == OWNER.lower()

# =========================================================
# ПОДПИСКА
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
    
    await message.answer(
        "🔒 <b>ТРЕБУЕТСЯ ПОДПИСКА</b>\n\n"
        f"Подпишись на канал:\n{CHANNEL_LINK}",
        reply_markup=subscribe_keyboard(),
        parse_mode="HTML"
    )
    return False

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
    kb.adjust(2)
    return kb.as_markup()

def donate_keyboard():
    kb = InlineKeyboardBuilder()
    for key, data in DONATE_PACKS.items():
        kb.button(text=f"{data['name']} — {data['stars']} ⭐", callback_data=f"donate:{key}")
    kb.button(text="⬅️ Назад", callback_data="menu")
    kb.adjust(1)
    return kb.as_markup()

# =========================================================
# КОМАНДА /start
# =========================================================
@DP.message(Command("start"))
async def start_command(message: Message):
    await register_user(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.first_name or ""
    )
    
    if not await require_subscription(message):
        return
    
    user = await get_user(message.from_user.id)
    available = await get_available_images(message.from_user.id)
    
    await message.answer(
        f"🤖 <b>ИИ-АССИСТЕНТ</b>\n\n"
        f"Привет, <b>{html.escape(message.from_user.first_name)}</b>!\n"
        f"🖼️ Доступно фото: <b>{available}</b>\n"
        f"💰 Цена фото: <b>{IMAGE_PRICE} ⭐</b>\n\n"
        f"💬 Просто напиши мне вопрос!\n"
        f"🖼️ Создай фото командой:\n"
        f"<code>/image описание фото</code>\n\n"
        f"📰 /news — последние новости\n"
        f"🌤️ /weather Москва — погода\n"
        f"💰 /crypto — курсы криптовалют",
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )

@DP.callback_query(F.data == "check_sub")
async def check_sub_callback(callback: CallbackQuery):
    await callback.answer()
    if await check_subscription(callback.from_user.id):
        await callback.message.edit_text(
            "✅ Подписка подтверждена!",
            reply_markup=main_keyboard(),
            parse_mode="HTML"
        )
    else:
        await callback.message.answer("❌ Подписка не найдена.", reply_markup=subscribe_keyboard())

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
        f"🖼️ Доступно фото: <b>{available}</b>\n"
        f"🖼️ Использовано за неделю: <b>{user['images_used_week']}/{FREE_IMAGES_PER_WEEK}</b>\n"
        f"⭐ Потрачено Stars: <b>{user['total_donated']}</b>",
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )

# =========================================================
# ЧАТ С ИИ (БЕСПЛАТНО)
# =========================================================
@DP.callback_query(F.data == "chat")
async def chat_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "💬 <b>ЧАТ С ИИ</b>\n\n"
        "Просто напиши мне любое сообщение!\n\n"
        "Я отвечу на любой вопрос, помогу с идеями, объясню сложные вещи.",
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )

# Обработка сообщений (бесплатно)
@DP.message(F.text & ~F.text.startswith('/'))
async def handle_chat(message: Message):
    if not await require_subscription(message):
        return
    
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer("❌ Напиши /start")
        return
    
    # Обновляем статистику
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET total_requests = total_requests + 1 WHERE user_id = ?", 
                       (message.from_user.id,))
        await db.commit()
    
    # Отправляем "печатает"
    await BOT.send_chat_action(message.chat.id, "typing")
    
    # Здесь должен быть запрос к OpenAI
    # Пока эмуляция (для теста)
    await asyncio.sleep(1)
    
    await message.answer(
        f"🤖 <b>ИИ ОТВЕЧАЕТ</b>\n\n"
        f"Ты спросил: {html.escape(message.text)}\n\n"
        f"Это тестовый ответ. Для работы с реальным ИИ нужен ключ OpenAI.",
        parse_mode="HTML"
    )

# =========================================================
# ГЕНЕРАЦИЯ ФОТО (ПЛАТНАЯ)
# =========================================================
@DP.message(Command("image"))
async def image_command(message: Message):
    if not await require_subscription(message):
        return
    
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "🖼️ <b>ГЕНЕРАЦИЯ ФОТО</b>\n\n"
            "<code>/image описание фото</code>\n\n"
            "Пример: <code>/image красивый закат на море</code>\n\n"
            f"Цена: <b>{IMAGE_PRICE} ⭐</b>\n"
            f"Бесплатно: <b>{FREE_IMAGES_PER_WEEK} фото</b> в неделю",
            parse_mode="HTML"
        )
        return
    
    prompt = parts[1]
    user = await get_user(message.from_user.id)
    available = await get_available_images(message.from_user.id)
    
    if available <= 0:
        kb = InlineKeyboardBuilder()
        kb.button(text="⭐ Купить фото", callback_data="donate")
        kb.adjust(1)
        
        await message.answer(
            f"❌ <b>НЕТ ДОСТУПНЫХ ФОТО</b>\n\n"
            f"Бесплатные лимит: {FREE_IMAGES_PER_WEEK} фото в неделю\n"
            f"Цена: {IMAGE_PRICE} ⭐ за фото\n\n"
            f"Купи пак фото за Stars!",
            reply_markup=kb.as_markup(),
            parse_mode="HTML"
        )
        return
    
    # Проверяем, бесплатное или платное
    is_free = user['images_used_week'] < FREE_IMAGES_PER_WEEK
    
    if is_free:
        # Бесплатное фото
        await message.answer(f"🖼️ <b>ГЕНЕРИРУЮ ФОТО...</b>\n\n🔹 Бесплатное (осталось: {available-1})", parse_mode="HTML")
        
        async with aiosqlite.connect(DB) as db:
            await db.execute("UPDATE users SET images_used_week = images_used_week + 1 WHERE user_id = ?",
                           (message.from_user.id,))
            await db.commit()
        
        # Генерируем фото (эмуляция)
        await asyncio.sleep(2)
        
        await message.answer(
            f"🖼️ <b>ФОТО ГОТОВО!</b>\n\n"
            f"Запрос: <i>{html.escape(prompt)}</i>\n\n"
            f"🔹 Бесплатное (осталось: {available-1})",
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

# =========================================================
# НОВОСТИ
# =========================================================
@DP.callback_query(F.data == "news")
async def news_callback(callback: CallbackQuery):
    await callback.answer()
    
    # Эмуляция новостей
    news = [
        {"title": "Курс Bitcoin вырос до $70,000", "description": "За последние сутки криптовалюта подорожала на 5%...", "url": "#"},
        {"title": "Telegram запускает новые функции для ботов", "description": "Разработчики Telegram анонсировали...", "url": "#"},
        {"title": "ИИ научился генерировать реалистичные фото", "description": "Новая модель OpenAI поражает...", "url": "#"},
    ]
    
    text = "📰 <b>ПОСЛЕДНИЕ НОВОСТИ</b>\n\n"
    for i, item in enumerate(news, 1):
        text += f"{i}. <b>{item['title']}</b>\n"
        text += f"   {item['description'][:100]}...\n\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=main_keyboard(),
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
        await message.answer("🌤️ <code>/weather ГОРОД</code>", parse_mode="HTML")
        return
    
    city = parts[1]
    
    # Эмуляция погоды
    temp = random.randint(-10, 35)
    conditions = ["Ясно", "Облачно", "Дождь", "Снег", "Туман"]
    condition = random.choice(conditions)
    
    await message.answer(
        f"🌤️ <b>ПОГОДА В {city.upper()}</b>\n\n"
        f"🌡️ Температура: <b>{temp}°C</b>\n"
        f"☁️ {condition}\n",
        parse_mode="HTML"
    )

# =========================================================
# КРИПТО
# =========================================================
@DP.callback_query(F.data == "crypto")
async def crypto_callback(callback: CallbackQuery):
    await callback.answer()
    
    # Эмуляция крипто цен
    crypto = [
        {"name": "Bitcoin", "symbol": "BTC", "price": 70000, "change": "+5.2%"},
        {"name": "Ethereum", "symbol": "ETH", "price": 3500, "change": "+3.1%"},
        {"name": "Solana", "symbol": "SOL", "price": 180, "change": "-2.5%"},
    ]
    
    text = "💰 <b>КУРСЫ КРИПТОВАЛЮТ</b>\n\n"
    for c in crypto:
        emoji = "📈" if "+" in c['change'] else "📉"
        text += f"{c['name']} ({c['symbol']}): ${c['price']:,} {emoji} {c['change']}\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )

# =========================================================
# ДОНАТ (ПОКУПКА ФОТО)
# =========================================================
@DP.callback_query(F.data == "donate")
async def donate_callback(callback: CallbackQuery):
    await callback.answer()
    user = await get_user(callback.from_user.id)
    available = await get_available_images(callback.from_user.id)
    
    await callback.message.edit_text(
        f"⭐ <b>КУПИТЬ ФОТО</b>\n\n"
        f"🖼️ Доступно фото: <b>{available}</b>\n"
        f"💰 Цена: <b>{IMAGE_PRICE} ⭐</b> за фото\n\n"
        f"Выбери пак фото:",
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

@DP.pre_checkout_query()
async def pre_checkout_query(query: PreCheckoutQuery):
    await query.answer(ok=True)

@DP.message(F.successful_payment)
async def successful_payment(message: Message):
    payload = message.successful_payment.invoice_payload
    
    if payload.startswith("image:"):
        prompt = payload.split(":", 1)[1]
        # Генерация фото (эмуляция)
        await message.answer(
            f"🖼️ <b>ФОТО ГОТОВО!</b>\n\n"
            f"Запрос: <i>{html.escape(prompt)}</i>\n\n"
            f"⭐ Оплачено: {IMAGE_PRICE} ⭐",
            parse_mode="HTML"
        )
    
    elif payload.startswith("donate:"):
        key = payload.split(":")[1]
        pack = DONATE_PACKS.get(key)
        if pack:
            async with aiosqlite.connect(DB) as db:
                await db.execute("UPDATE users SET extra_images = extra_images + ? WHERE user_id = ?",
                               (pack['images'], message.from_user.id))
                await db.execute("UPDATE users SET total_donated = total_donated + ? WHERE user_id = ?",
                               (pack['stars'], message.from_user.id))
                await db.execute("INSERT INTO donations (user_id, pack_id, stars, created_at) VALUES (?, ?, ?, ?)",
                               (message.from_user.id, key, pack['stars'], int(time.time())))
                await db.commit()
            
            await message.answer(
                f"✅ <b>ПОКУПКА УСПЕШНА!</b>\n\n"
                f"📦 Пак: {pack['name']}\n"
                f"🖼️ Фото: <b>+{pack['images']}</b>\n"
                f"⭐ Потрачено: <b>{pack['stars']}</b>",
                parse_mode="HTML"
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
        "Промокод даёт бесплатные фото!",
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )

@DP.message(Command("promo"))
async def promo_command(message: Message):
    if not await require_subscription(message):
        return
    
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("🎟️ Использование: <code>/promo КОД</code>", parse_mode="HTML")
        return
    
    code = parts[1].upper()
    
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM promo_codes WHERE code = ?", (code,))
        promo = await cur.fetchone()
        
        if not promo:
            await message.answer("❌ Промокод не найден!")
            return
        
        cur2 = await db.execute("SELECT 1 FROM promo_uses WHERE code = ? AND user_id = ?", (code, message.from_user.id))
        if await cur2.fetchone():
            await message.answer("❌ Ты уже использовал этот промокод!")
            return
        
        if promo['used'] >= promo['activations']:
            await message.answer("❌ Лимит активаций исчерпан!")
            return
        
        await db.execute("INSERT INTO promo_uses (code, user_id) VALUES (?, ?)", (code, message.from_user.id))
        await db.execute("UPDATE promo_codes SET used = used + 1 WHERE code = ?", (code,))
        await db.execute("UPDATE users SET extra_images = extra_images + ? WHERE user_id = ?",
                       (promo['images'], message.from_user.id))
        await db.commit()
    
    await message.answer(
        f"🎉 <b>ПРОМОКОД АКТИВИРОВАН!</b>\n\n"
        f"🖼️ Получено фото: <b>+{promo['images']}</b>",
        parse_mode="HTML"
    )

# =========================================================
# АДМИНКА (ТОЛЬКО ДЛЯ @foqlu)
# =========================================================
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
        await message.answer("❌ Неверные данные!")
        return
    
    async with aiosqlite.connect(DB) as db:
        try:
            await db.execute("INSERT INTO promo_codes (code, images, activations, used, created_at) VALUES (?, ?, ?, 0, ?)",
                           (code, images, limit, int(time.time())))
            await db.commit()
        except:
            await message.answer("❌ Промокод уже существует!")
            return
    
    await message.answer(
        f"✅ <b>ПРОМОКОД СОЗДАН!</b>\n\n"
        f"🎟️ Код: <code>{code}</code>\n"
        f"🖼️ Фото: <b>{images}</b>\n"
        f"👥 Активаций: <b>{limit}</b>",
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
            "<code>/post ТЕКСТ ПОСТА</code>\n\n"
            "После создания бот отправит пост всем пользователям.",
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
            await BOT.send_message(row[0], 
                f"📢 <b>ОБЪЯВЛЕНИЕ</b>\n\n{text}\n\n---\n🤖 ИИ-Ассистент",
                parse_mode="HTML")
            sent += 1
            await asyncio.sleep(0.05)
        except:
            pass
    
    await message.answer(f"✅ Пост отправлен <b>{sent}</b> пользователям!", parse_mode="HTML")

@DP.message(Command("stats"))
async def stats_command(message: Message):
    if not is_owner(message.from_user):
        await message.answer("❌ Только для владельца!")
        return
    
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT COUNT(*) FROM users")
        users = (await cur.fetchone())[0]
        
        cur = await db.execute("SELECT SUM(total_requests) FROM users")
        total_requests = (await cur.fetchone())[0] or 0
        
        cur = await db.execute("SELECT SUM(total_donated) FROM users")
        total_donated = (await cur.fetchone())[0] or 0
    
    await message.answer(
        f"📊 <b>СТАТИСТИКА</b>\n\n"
        f"👥 Пользователей: <b>{users}</b>\n"
        f"💬 Всего запросов: <b>{total_requests}</b>\n"
        f"⭐ Получено Stars: <b>{total_donated}</b>",
        parse_mode="HTML"
    )

@DP.message(Command("ban"))
async def ban_command(message: Message):
    if not is_owner(message.from_user):
        return
    
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("Использование: <code>/ban USER_ID</code>", parse_mode="HTML")
        return
    
    try:
        user_id = int(parts[1])
    except:
        await message.answer("❌ Неверный ID!")
        return
    
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET banned = 1 WHERE user_id = ?", (user_id,))
        await db.commit()
    
    await message.answer(f"🚫 Пользователь <code>{user_id}</code> забанен!", parse_mode="HTML")

@DP.message(Command("unban"))
async def unban_command(message: Message):
    if not is_owner(message.from_user):
        return
    
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("Использование: <code>/unban USER_ID</code>", parse_mode="HTML")
        return
    
    try:
        user_id = int(parts[1])
    except:
        await message.answer("❌ Неверный ID!")
        return
    
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE users SET banned = 0 WHERE user_id = ?", (user_id,))
        await db.commit()
    
    await message.answer(f"✅ Пользователь <code>{user_id}</code> разбанен!", parse_mode="HTML")

# =========================================================
# МЕНЮ
# =========================================================
@DP.callback_query(F.data == "menu")
async def menu_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "🤖 <b>ИИ-АССИСТЕНТ</b>\n\n"
        "Выбери действие:",
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )

# =========================================================
# ЗАПУСК
# =========================================================
async def main():
    await init_db()
    print("=" * 60)
    print("🤖 ИИ-АССИСТЕНТ + ГЕНЕРАЦИЯ ФОТО")
    print(f"👑 OWNER: @{OWNER}")
    print(f"📢 КАНАЛ: {CHANNEL_LINK}")
    print(f"🖼️ Бесплатных фото в неделю: {FREE_IMAGES_PER_WEEK}")
    print(f"💰 Цена фото: {IMAGE_PRICE} ⭐")
    print("=" * 60)
    await DP.start_polling(BOT)

if __name__ == "__main__":
    asyncio.run(main())
