import asyncio
import sqlite3

from aiogram import Bot, F, Router, types
from aiogram.filters.command import Command

router = Router()
router.message.filter(F.from_user.id.in_([760709790, 378790166]))
routers = [router]

NAMES = {
    2061148502: "Барбаччи Анастасия",
    "SOSchlenoSOS": "Батин Платон",  # закрыт
    1515192079: "Борисов Александр",
    855323286: "Быков Денис",
    "MaxMerzyl": "Голубенко Максим",  # закрыт
    5278809823: "Горбунова Ксения",
    1000131290: "Дерибин Матвей",
    1057129270: "Дзикевич Максим",
    592699018: "Ермохин Андрей",
    810636482: "Занин Никита",
    1033407535: "Иванов Никита",
    874865029: "Казанцев Арсений",
    748197936: "Канев Александр",
    378790166: "Колесников Алексей",
    "nhyseq": "Королёв Олег",  # мб вообще нет сообщений
    2117990099: "Кузнецов Александр",
    1493231220: "Курохтин Михаил",
    "Skrea1m": "Лихачёв Алексей",  # закрыт
    5216880345: "Лучшев Вадим",
    1028517848: "Лясин Иван",
    "Prapor02": "Магомедов Пайзула",  # закрыт
    754601226: "Макаров Вячеслав",
    760709790: "Олейник Данил",
    430354302: "Пшеничнов Святослав",
    861064904: "Ребриков Артём",
    691608678: "Рыбаченок Вадим",
    7148607418: "Сафронов Денис",
    "VovseNeTorch": "Селиверстов Дмитрий",  # нет сообщений мб
    5461434577: "Сон Владимир",
    1365932181: "Трубников Ярослав",
    6443296662: "Ушакова Ника",
    1002963862: "Штриков Дмитрий",
}
ANSWER_OPTIONS = ["На паре", "Опаздываю", "Отсутствую"]
TARGET_CHAT = "-1002183941184_2140"

actual_poll_id = -1

# Подключаемся к базе данных (или создаем её, если она не существует)
conn = sqlite3.connect("polls.db")
cursor = conn.cursor()

# Создаем таблицу для хранения данных о голосах
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS poll_answers (
    user_id INTEGER,
    user_name TEXT,
    option_id INTEGER
)
"""
)
conn.commit()


def clear_poll_answers():
    """Функция для очистки таблицы голосов"""
    cursor.execute("DELETE FROM poll_answers")
    conn.commit()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет, чтобы запустить голосование введи команду /presence")


@router.message(Command("presence"))
async def cmd_presence(message: types.Message, bot: Bot):
    clear_poll_answers()

    await message.answer("Опрос запущен")
    result = await bot.send_poll(
        "-1002434066039_5",  # todo: Заменить на константу
        question="Присутствие на паре",
        options=ANSWER_OPTIONS,
        is_anonymous=False,
        open_period=5,  # todo: Надо сделать больше времени
    )
    global actual_poll_id
    actual_poll_id = result.poll.id

    # Запускаем таймер на 20 минут для отправки результатов
    await send_poll_results_after_delay(
        bot, "-1002434066039_5", 5
    )  # 20 минут = 1200 секунд


async def send_poll_results_after_delay(bot: Bot, chat_id: int, delay: int):
    """Функция для отправки результатов спустя 10 минут"""
    await asyncio.sleep(delay)  # Ожидаем заданное количество секунд (10 минут)
    cursor.execute("SELECT user_id, user_name, option_id FROM poll_answers")
    results = cursor.fetchall()

    if results:
        result_message = "Результаты голосования:\n\n"

        for user_id, user_name, option_id in results:
            result_message += (
                f"{user_name} ({user_id}) выбрал(а) {ANSWER_OPTIONS[option_id]}\n"
            )

        await bot.send_message(chat_id, result_message)
    else:
        await bot.send_message(chat_id, "Еще никто не проголосовал.")


@router.poll_answer()
async def poll_answer(poll_answer: types.PollAnswer):
    """Обработчик события отправки голосов"""
    if actual_poll_id != poll_answer.poll_id:
        return
    if (
        poll_answer.user.id not in NAMES.keys()
        and poll_answer.user.username not in NAMES.keys()
    ):
        return

    user_id = poll_answer.user.id
    user_name = poll_answer.user.full_name
    selected_options = poll_answer.option_ids  # Список индексов выбранных вариантов

    # Сохраняем данные в базу
    for option_id in selected_options:
        cursor.execute(
            "INSERT INTO poll_answers (user_id, user_name, option_id) VALUES (?, ?, ?)",
            (user_id, user_name, option_id),
        )
        conn.commit()

        print(
            f"Пользователь {user_name} ({user_id}) проголосовал. Выбранная опция: {ANSWER_OPTIONS[int(option_id)]}"
        )
