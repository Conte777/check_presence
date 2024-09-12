import logging
import sys
from asyncio import run

from bot_init import bot_initialization
from handlers import routers


async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    await bot_initialization(routers)


if __name__ == "__main__":
    try:
        run(main())
    except KeyboardInterrupt:
        print("Бот завершил работу принудительно")
