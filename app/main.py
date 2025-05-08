import asyncio

from app.lis.factory import handle_restart_parse_after_reboot
from app.lis.dispatchers import dp

from app.telegram.bot_config import bot


async def main() -> None:
    print("Бот запускается...")

    await handle_restart_parse_after_reboot()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
