import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message


TOKEN = os.getenv("8944917133:AAHzyZPUwfVahJEko0gOapBGh0nCxjcDcmY")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN не найден")


bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "⚽ Добро пожаловать в футбольный квиз!\n\n"
        "Напиши «Квиз», чтобы начать."
    )


@dp.message()
async def message_handler(message: Message):
    if message.text and message.text.lower().strip() == "квиз":
        await message.answer(
            "🎯 Квиз скоро начнётся!\n\n"
            "⭐ Рейтинг: 90\n"
            "🌍 Сборная: Испания\n"
            "⚽ Позиция: ПВ\n\n"
            "⏳ Осталось времени: 5:00"
        )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
