from app.lis.tasks import (
    start_listener_for_user,
    stop_listener_for_user,
)
from app.lis import crud as lis_crud

from app.logger import logger


async def handle_start_parse(tg_id: int) -> None:
    conditions = await lis_crud.get_conditions_for_user(tg_id=tg_id)

    lis_user = await lis_crud.check_exist_user_or_not(tg_id=tg_id)

    await start_listener_for_user(
        tg_id=tg_id,
        lis_token=lis_user.lis_token,
        conditions=conditions,
    )


async def handle_stop_parse(tg_id: int) -> None:
    await stop_listener_for_user(tg_id=tg_id)


async def handle_restart_parse_after_reboot() -> None:
    all_active_parse_models = await lis_crud.get_all_active_parse_models()

    if not all_active_parse_models:
        logger.info("Нет активных парсов для перезапуска.")
        return

    logger.info(f"Найдено {len(all_active_parse_models)} парсов для перезапуска.")

    for active_parse in all_active_parse_models:
        await handle_start_parse(tg_id=active_parse.tg_id)

    logger.info("Перезапуск завершён.")
