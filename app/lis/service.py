import json
import asyncio

import httpx
import websockets

from app.lis.schemas import ItemConditionsSchema
from app.lis.utils import (
    check_item_against_conditions,
    format_item_message,
    foramt_message,
)
from app.lis import crud as lis_crud
from app.lis import constants

from app.config import settings
from app.logger import logger

from app.db import ParsedItems


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


active_websockets: dict[int, websockets.ClientProtocol] = {}


async def run_node_listener(
    lis_token: str,
    conditions: ItemConditionsSchema,
    tg_id: int,
) -> None:
    uri = "ws://ws-server:8080"

    try:
        async with websockets.connect(uri) as websocket:
            active_websockets[tg_id] = websocket

            await websocket.send(json.dumps({"type": "start", "lis_token": lis_token}))

            logger.info(f"🔌 Подключён к WS для пользователя {tg_id}")

            while True:
                try:
                    message = await websocket.recv()

                    decoded = json.loads(message)

                    if decoded.get("type") != "event":
                        continue

                    item_data = decoded.get("data")
                    if not item_data:
                        continue

                    if check_item_against_conditions(item_data, conditions.items):
                        event = item_data.get("event")

                        if event in {
                            "obtained_skin_added",
                            "obtained_skin_price_changed",
                        }:
                            formatted_message = format_item_message(
                                item=item_data, event=event
                            )

                            await create_record_about_founded_item(
                                tg_id=tg_id,
                                item_data=item_data,
                                event=event,
                            )

                            await send_telegram_message(
                                tg_id=tg_id, message=formatted_message
                            )

                except json.JSONDecodeError:
                    logger.warning(f"❌ Некорректный JSON от WS-сервера: {message}")

                except websockets.ConnectionClosed:
                    logger.error(f"🔴 WS-соединение закрыто для {tg_id}")
                    break

                except Exception as e:
                    logger.exception(
                        f"❌ Ошибка во время парсинга WS-сообщения для {tg_id}: {e}"
                    )
                    await asyncio.sleep(1)

    except Exception as e:
        logger.exception(f"❌ Ошибка подключения к WS-серверу: {e}")

    finally:
        active_websockets.pop(tg_id, None)


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


async def fetch_usd_to_rub():
    url = "https://www.cbr-xml-daily.ru/daily_json.js"

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)
            data = response.json()

            new_rate = data["Valute"]["USD"]["Value"]
            constants.USD_TO_RUB = new_rate
            logger.info(f"🔄 Курс доллара обновлён: {new_rate}")

    except Exception as e:
        logger.error(f"❌ Ошибка при получении курса доллара: {e}")


async def create_record_about_founded_item(
    tg_id: int,
    item_data: dict,
    event: str,
) -> ParsedItems:
    return await lis_crud.create_record_about_parsed_skin(
        tg_id=tg_id,
        item_data=item_data,
        event=event,
    )


async def get_parsed_items_messages(tg_id: int, limit: int) -> list[str]:
    parsed_items: list[ParsedItems] = await lis_crud.get_last_parsed_items(
        tg_id=tg_id, limit=limit
    )

    if not parsed_items:
        return ["🔍 Записи не найдены."]

    return foramt_message(parsed_items=parsed_items)
