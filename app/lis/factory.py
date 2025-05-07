from app.lis.tasks import (
    start_listener_for_user,
    stop_listener_for_user,
)
from app.lis.service import fetch_ws_token
from app.lis import crud as lis_crud


async def handle_start_parse(tg_id: int) -> None:
    conditions = await lis_crud.get_conditions_for_user(tg_id=tg_id)

    lis_user = await lis_crud.check_exist_user_or_not(tg_id=tg_id)

    ws_token = await fetch_ws_token(lis_token=lis_user.lis_token)

    await start_listener_for_user(
        tg_id=tg_id,
        ws_token=ws_token,
        conditions=conditions,
    )


async def handle_stop_parse(tg_id: int) -> None:
    await stop_listener_for_user(tg_id=tg_id)
