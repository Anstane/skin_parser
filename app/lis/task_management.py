import asyncio

from app.lis.service import run_node_listener
from app.lis.schemas import ItemConditionsSchema
from app.lis import crud as lis_crud

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
            print(f"🔴 Listener для {tg_id} остановлен")

    task = asyncio.create_task(
        run_node_listener(ws_token=ws_token, conditions=conditions)
    )
    active_listeners[tg_id] = task
    print(f"🟢 Listener для {tg_id} запущен")

    await lis_crud.set_parse_status(tg_id=tg_id, active=True)


async def stop_listener_for_user(tg_id: int):
    task = active_listeners.get(tg_id)
    if task:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            print(f"🔴 Listener для {tg_id} остановлен")

        del active_listeners[tg_id]

    await lis_crud.set_parse_status(tg_id=tg_id, active=False)
