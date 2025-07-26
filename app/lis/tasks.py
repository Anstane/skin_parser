import asyncio
import json

from app.lis.service import (
    run_node_listener,
    send_telegram_message,
    fetch_usd_to_rub,
    active_websockets,
)
from app.lis.schemas import ItemConditionsSchema
from app.lis import crud as lis_crud

from app.logger import logger

active_listeners: dict[int, asyncio.Task] = {}
active_watchdogs: dict[int, asyncio.Task] = {}


async def start_listener_for_user(
    tg_id: int,
    lis_token: str,
    conditions: ItemConditionsSchema,
):
    if tg_id in active_listeners:
        task = active_listeners[tg_id]
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            await send_telegram_message(tg_id, f"🔴 Парс для {tg_id} остановлен")

            logger.info(f"🔴 Парс для {tg_id} остановлен")

    task = asyncio.create_task(
        run_node_listener(
            lis_token=lis_token,
            conditions=conditions,
            tg_id=tg_id,
        )
    )
    active_listeners[tg_id] = task

    if tg_id in active_watchdogs:
        active_watchdogs[tg_id].cancel()

    watchdog_task = asyncio.create_task(watchdog_for_user(tg_id))

    active_watchdogs[tg_id] = watchdog_task

    await send_telegram_message(tg_id, f"🟢 Парс для {tg_id} запущен")

    logger.info(f"🟢 Парс для {tg_id} запущен")

    await lis_crud.set_parse_status(tg_id=tg_id, active=True)


async def stop_listener_for_user(tg_id: int):
    task = active_listeners.pop(tg_id, None)
    if task:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            logger.info(f"🔴 Парс для {tg_id} остановлен")

    websocket = active_websockets.pop(tg_id, None)
    if websocket:
        try:
            await websocket.send(json.dumps({"type": "stop"}))
            await websocket.close()
            logger.info(f"🔌 WebSocket для {tg_id} закрыт")
        except Exception as e:
            logger.warning(f"❌ Ошибка при закрытии WS {tg_id}: {e}")

    watchdog = active_watchdogs.pop(tg_id, None)
    if watchdog:
        watchdog.cancel()
        try:
            await watchdog
        except asyncio.CancelledError:
            logger.info(f"🔕 Сторож для {tg_id} остановлен")

    await lis_crud.set_parse_status(tg_id=tg_id, active=False)


async def watchdog_for_user(tg_id: int, check_interval: int = 30):
    while True:
        await asyncio.sleep(check_interval)

        task = active_listeners.get(tg_id)

        if not task or task.done():
            await send_telegram_message(
                tg_id, "⚠️ Парсинг неожиданно остановился. Перезапускаем..."
            )

            logger.warning(f"⚠️ Парсинг для {tg_id} завершился. Перезапускаем...")

            conditions = await lis_crud.get_conditions_for_user(tg_id=tg_id)

            lis_user = await lis_crud.check_exist_user_or_not(tg_id=tg_id)

            await start_listener_for_user(
                tg_id=tg_id,
                lis_token=lis_user.lis_token,
                conditions=conditions,
            )

            break


async def run_exchange_rate_updater():
    while True:
        await fetch_usd_to_rub()
        await asyncio.sleep(3600)
