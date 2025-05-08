import json
import asyncio

import httpx

from app.lis.schemas import ItemConditionsSchema
from app.lis.utils import (
    check_item_against_conditions,
    format_item_message,
)

from app.config import settings


async def get_user_balance(lis_token: str) -> dict:
    url = "https://api.lis-skins.com/v1/user/balance"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {lis_token}",
    }

    async with httpx.AsyncClient() as http_client:
        response = await http_client.get(url=url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            return data.get("data", {})

        else:
            return {"error": "Ошибка при получении баланса!"}


async def send_request_for_skins(data: dict, lis_token: str) -> dict:
    base_url = "https://api.lis-skins.com/v1/market/search"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {lis_token}",
    }

    data["game"] = "csgo"

    query_parts = []
    for key, value in data.items():
        if isinstance(value, list):
            for item in value:
                query_parts.append(f"{key}={item}")
        else:
            query_parts.append(f"{key}={value}")

    query_string = "&".join(query_parts)
    full_url = f"{base_url}?{query_string}"

    async with httpx.AsyncClient() as http_client:
        response = await http_client.get(
            url=full_url,
            headers=headers,
        )
        return response.json()


async def fetch_ws_token(lis_token: str) -> str:
    url = "https://api.lis-skins.com/v1/user/get-ws-token"

    headers = {"Authorization": f"Bearer {lis_token}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url=url, headers=headers)
        return response.json()["data"]["token"]


async def run_node_listener(
    ws_token: str,
    conditions: ItemConditionsSchema,
    tg_id: int,
) -> None:
    process = await asyncio.create_subprocess_exec(
        "node",
        "/app/app/lis/js_client/client.js",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    process.stdin.write((ws_token + "\n").encode())
    await process.stdin.drain()

    while True:
        line = await process.stdout.readline()
        if not line:
            break

        decoded_line = line.decode("utf-8").strip()
        if not decoded_line:
            continue

        try:
            event_data = json.loads(decoded_line)

            if check_item_against_conditions(event_data, conditions.items):
                event = event_data["event"]

                if event in {"obtained_skin_added", "obtained_skin_price_changed"}:
                    message = format_item_message(item=event_data, event=event)

                    await send_telegram_message(tg_id=tg_id, message=message)

        except json.JSONDecodeError as e:
            print(f"❌ Ошибка декодирования JSON: {e}")

    await process.wait()


async def send_telegram_message(tg_id: int, message: str) -> None:
    async with httpx.AsyncClient() as http_client:
        token = settings.TELEGRAM.TOKEN
        response = await http_client.post(
            url=f"https://api.telegram.org/bot{token}/sendMessage",
            data={
                "chat_id": tg_id,
                "text": message,
                "parse_mode": "HTML",
            },
        )
