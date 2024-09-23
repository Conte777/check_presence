import asyncio
import sqlite3

from aiogram import Bot, F, Router, types
from aiogram.filters.command import Command

from config import (
    ADMINS_IDS,
    ANSWER_OPTIONS,
    ANSWER_OPTIONS_FOR_PRINT,
    AWAIT_ANSWER_TIME,
    STUDENTS_NAMES,
    TARGET_CHAT,
    THREAD_ID,
)

router = Router()
router.message.filter(F.from_user.id.in_(ADMINS_IDS))
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
        TARGET_CHAT,
        question="Присутствие на паре",
        options=ANSWER_OPTIONS,
        is_anonymous=False,
        open_period=AWAIT_ANSWER_TIME,
        message_thread_id=THREAD_ID,
    )

    # Запускаем таймер
    await send_poll_results_after_delay(
        bot=bot, delay=AWAIT_ANSWER_TIME + 1, poll_id=result.poll.id
    )


async def send_poll_results_after_delay(bot: Bot, delay: int, poll_id: int):
    """Функция для отправки результатов спустя время"""
    await asyncio.sleep(delay)  # Ожидаем заданное количество секунд

    result_message = "Результаты голосования:\n\n"  # Итоговое сообщение
    voted_users = []  # Сюда будут пихаться имена тех, кто проголосовал
    for i in range(len(ANSWER_OPTIONS)):
        # Для каждого варианта отдельная группа
        cursor.execute(
            """SELECT user_fullname
            FROM poll_answers 
            WHERE poll_id = ? AND option_id = ?
            ORDER BY user_fullname ASC""",
            (poll_id, i),
        )
        results = cursor.fetchall()

        result_message += (
            f"Количество человек {ANSWER_OPTIONS_FOR_PRINT[i]}: {len(results)}\n"
        )
        if results:
            for user_fullname in results:
                result_message += f"{user_fullname[0]}\n"
                voted_users.append(user_fullname[0])
        result_message += "\n"

    # Добавляем раздел с непроголосовавшими
    not_voted_users = list(set(STUDENTS_NAMES.values()) - set(voted_users))
    if not_voted_users:
        not_voted_users.sort()
        result_message += f"Непроголосовавшие люди: {len(not_voted_users)}\n"
        for user in not_voted_users:
            result_message += user + "\n"

    # Отправляем итоговое сообщение
    await bot.send_message(TARGET_CHAT, result_message, message_thread_id=THREAD_ID)
    # Чистим базу данных от уже устаревшего опроса
    cursor.execute(
        "DELETE FROM poll_answers WHERE poll_id = ?",
        (poll_id,),
    )
    conn.commit()


@router.poll_answer()
async def poll_answer(poll_answer: types.PollAnswer):
    """Обработчик события отправки голосов"""
    if (
        poll_answer.user.id not in STUDENTS_NAMES.keys()
        and poll_answer.user.username not in STUDENTS_NAMES.keys()
    ):
        return

    user_id = poll_answer.user.id
    username = poll_answer.user.username
    user_fullname = STUDENTS_NAMES.get(
        user_id, STUDENTS_NAMES.get(username, "not_found_userfullname")
    )
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
                """INSERT INTO poll_answers (user_id, user_fullname, option_id, poll_id) 
                VALUES (?, ?, ?, ?)""",
                (user_id, user_fullname, option, poll_id),
            )
        conn.commit()

        print(f"{user_fullname} ({user_id}) {ANSWER_OPTIONS_FOR_PRINT[int(option)]}")
