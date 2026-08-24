import os
import random
import asyncio
import time

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message


TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

print("TOKEN EXISTS:", bool(TOKEN))
print("TOKEN LENGTH:", len(TOKEN) if TOKEN else 0)

if not TOKEN:
    raise RuntimeError("TOKEN IS EMPTY")


bot = Bot(token=TOKEN)
dp = Dispatcher()


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


games = {}
timers = {}
ROUND_TIME = 300


def new_round(user_id):
    player = random.choice(PLAYERS)
    games[user_id] = player
    timers[user_id] = time.time()

    asyncio.create_task(timer_task(user_id))

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

    start_time = timers.get(user_id)

    if start_time is not None:
        elapsed = time.time() - start_time

        if elapsed >= ROUND_TIME:
            player = games[user_id]

            await message.answer(
                f"⏰ ВРЕМЯ ВЫШЛО!\n\n"
                f"⚽ Правильный ответ: {player['name']}"
            )

            player = new_round(user_id)
            await message.answer(question(player))
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


async def timer_task(user_id):
    start_time = timers.get(user_id)

    if start_time is None:
        return

    await asyncio.sleep(ROUND_TIME)

    if timers.get(user_id) != start_time:
        return

    player = games.get(user_id)

    if player:
        try:
            await bot.send_message(
                user_id,
                f"⏰ ВРЕМЯ ВЫШЛО!\n\n"
                f"⚽ Правильный ответ: {player['name']}"
            )

            new_player = new_round(user_id)

            await bot.send_message(
                user_id,
                question(new_player)
            )

        except Exception as e:
            print(f"Timer error: {e}")


async def main():
    print("BOT STARTED")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
