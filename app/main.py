import asyncio

from app.lis.factory import handle_restart_parse_after_reboot
from app.lis.tasks import run_exchange_rate_updater
from app.lis.dispatchers import dp

from app.telegram.bot_config import bot

from app.logger import logger


async def main() -> None:
    logger.info("Бот запускается...")

    asyncio.create_task(run_exchange_rate_updater())

    await handle_restart_parse_after_reboot()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
