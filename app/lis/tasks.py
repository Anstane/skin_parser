import asyncio

from app.lis.service import run_node_listener, send_telegram_message
from app.lis.schemas import ItemConditionsSchema
from app.lis import crud as lis_crud

from app.logger import logger

active_listeners: dict[int, asyncio.Task] = {}


async def start_listener_for_user(
    tg_id: int,
    ws_token: str,
    conditions: ItemConditionsSchema,
):
    if tg_id in active_listeners:
        task = active_listeners[tg_id]
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            await send_telegram_message(tg_id, f"🔴 Парс для {tg_id} остановлен")

    task = asyncio.create_task(
        run_node_listener(
            ws_token=ws_token,
            conditions=conditions,
            tg_id=tg_id,
        )
    )
    active_listeners[tg_id] = task

    logger.info(active_listeners)

    await send_telegram_message(tg_id, f"🟢 Парс для {tg_id} запущен")

    await lis_crud.set_parse_status(tg_id=tg_id, active=True)


async def stop_listener_for_user(tg_id: int):
    task = active_listeners.pop(tg_id, None)
    if task:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    await lis_crud.set_parse_status(tg_id=tg_id, active=False)
