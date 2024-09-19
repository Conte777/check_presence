from typing import List, Optional

from aiogram import Bot, Dispatcher, Router, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import secret_enum
from handlers import close_connection


async def set_my_commands(bot: Bot) -> None:
    """Настройка отображаемых команд в боте"""

    Commands = [
        types.BotCommand(command="start", description="Начало работы"),
        types.BotCommand(command="presence", description="Запуск голосования"),
    ]
    await bot.set_my_commands(Commands, types.BotCommandScopeDefault())


async def set_my_description(bot: Bot) -> None:
    """Настройка описаний бота"""

    await bot.set_my_description("Бот для отслеживания посещений БПИ2403")

    await bot.set_my_short_description("Бот для отслеживания посещений БПИ2403")


async def on_startup(bot: Bot) -> None:
    """Что нужно сделать при запуске бота"""
    await set_my_commands(bot)
    await set_my_description(bot)


async def on_shutdown(bot: Bot) -> None:
    """Что нужно сделать при выключении бота"""
    await close_connection()


async def bot_initialization(routers: Optional[List[Router]] = None) -> None:
    # Объект хранилища
    storage = None
    # if sys.platform == "win32":
    # для локальных запусков
    storage = MemoryStorage()
    # else:
    # для запуска на сервере
    # storage = RedisStorage.from_url("redis://localhost:6379/0")
    dp = Dispatcher(storage=storage)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    if routers is not None:
        dp.include_routers(*routers)

    global bot
    bot = Bot(
        token=secret_enum.bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    await dp.start_polling(bot)
