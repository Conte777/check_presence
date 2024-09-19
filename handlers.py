import asyncio
import sqlite3
from typing import List

from aiogram import Bot, F, Router, types
from aiogram.filters.command import Command

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
    958255880: "Лихачёв Алексей",
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
AWAIT_ANSWER_TIME = 30  # в пределах от 1 до 600 секунд
ADMINS = [760709790, 378790166]


router = Router()
router.message.filter(F.from_user.id.in_(ADMINS))
routers = [router]

# Подключаемся к базе данных (или создаем её, если она не существует)
conn = sqlite3.connect("polls.db")
cursor = conn.cursor()

# Создаем таблицу для хранения данных о голосах
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS poll_answers (
    user_id INTEGER,
    user_fullname TEXT,
    option_id INTEGER,
    poll_id INTEGER
)
"""
)
conn.commit()


async def close_connection():
    """Закрываем соединение с базой данных"""
    conn.close()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет, чтобы запустить голосование введи команду /presence")


@router.message(Command("presence"))
async def cmd_presence(message: types.Message, bot: Bot):
    await message.answer("Опрос запущен")
    result = await bot.send_poll(
        "-1002434066039_5",  # todo: Заменить на константу
        question="Присутствие на паре (Тест, потыкайте все варианты)",
        options=ANSWER_OPTIONS,
        is_anonymous=False,
        open_period=AWAIT_ANSWER_TIME,  # todo: Надо сделать больше времени
    )

    # Запускаем таймер на 20 минут для отправки результатов
    await send_poll_results_after_delay(
        bot=bot, chat_id=ADMINS, delay=AWAIT_ANSWER_TIME + 1, poll_id=result.poll.id
    )  # 20 минут = 1200 секунд


async def send_poll_results_after_delay(
    bot: Bot, chats_id: List[int], delay: int, poll_id: int
):
    """Функция для отправки результатов спустя 10 минут"""
    await asyncio.sleep(delay)  # Ожидаем заданное количество секунд (10 минут)
    cursor.execute(
        "SELECT user_id, user_fullname, option_id FROM poll_answers WHERE poll_id = ? ORDER BY option_id DESC",
        (poll_id,),
    )
    results = cursor.fetchall()

    if results:
        result_message = "Результаты голосования:\n\n"

        for user_id, user_fullname, option_id in results:
            result_message += (
                f"{user_fullname} ({user_id}) выбрал(а) {ANSWER_OPTIONS[option_id]}\n"
            )
        for chat in chats_id:
            await bot.send_message(chat, result_message)

        cursor.execute(
            "DELETE FROM poll_answers WHERE poll_id = ?",
            (poll_id,),
        )
        conn.commit()
    else:
        for chat in chats_id:
            await bot.send_message(chat, "Еще никто не проголосовал.")


@router.poll_answer()
async def poll_answer(poll_answer: types.PollAnswer):
    """Обработчик события отправки голосов"""
    if (
        poll_answer.user.id not in NAMES.keys()
        and poll_answer.user.username not in NAMES.keys()
    ):
        return

    user_id = poll_answer.user.id
    username = poll_answer.user.username
    user_fullname = NAMES.get(user_id, NAMES.get(username, "not_found_username"))
    selected_options = poll_answer.option_ids
    poll_id = poll_answer.poll_id

    # Сохраняем ответ в базу
    for option in selected_options:
        cursor.execute(
            """SELECT * 
            FROM poll_answers
            WHERE poll_id = ? AND user_id = ?""",
            (poll_id, user_id),
        )
        result = cursor.fetchall()
        if result:
            cursor.execute(
                """UPDATE poll_answers 
                SET option_id = ? 
                WHERE poll_id = ? AND user_id = ? AND option_id != ?""",
                (option, poll_id, user_id, option),
            )
        else:
            cursor.execute(
                "INSERT INTO poll_answers (user_id, user_fullname, option_id, poll_id) VALUES (?, ?, ?, ?)",
                (user_id, user_fullname, option, poll_id),
            )
        conn.commit()

        print(
            f"Пользователь {user_fullname} ({user_id}) проголосовал. Выбранная опция: {ANSWER_OPTIONS[int(option)]}"
        )
