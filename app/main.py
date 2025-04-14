import asyncio

from app.telegram.dispatchers import dp
from app.telegram.bot_config import bot


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
