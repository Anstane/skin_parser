from datetime import datetime

from aiogram.types import Message

from app.lis.schemas import ConditionSchema
from app.lis.constants import USD_TO_RUB, MAX_MESSAGE_LENGTH

from app.db import ParsedItems

from app.logger import logger


async def send_first_skins(message: Message, skins: list) -> None:
    skins_to_send = skins[:10]
    full_message = ""

    for idx, skin in enumerate(skins_to_send):
        skin_text = (
            f"🎯 <b>{skin['name']}</b>\n" f"💰 <b>Цена:</b> {skin['price']} USD\n"
        )

        paint_seed = skin.get("item_paint_seed")
        if paint_seed:
            skin_text += f"🎲 <b>Paint Seed:</b> {skin['item_paint_seed']}\n"

        item_float = skin.get("item_float")
        if item_float is not None:
            skin_text += f"🌡️ <b>Float:</b> {float(item_float):.6f}\n"

        if skin.get("unlock_at"):
            skin_text += f"🔓 <b>Разблокируется:</b> {skin['unlock_at'][:10]} {skin['unlock_at'][11:19]}\n"
        else:
            skin_text += f"🔓 <b>Предмет разблокирован!</b>\n"

        skin_text += f"📅 <b>Добавлен:</b> {skin['created_at'][:10]} {skin['created_at'][11:19]}\n"

        if skin.get("name_tag"):
            skin_text += f"🏷️ <b>Name Tag:</b> {skin['name_tag']}"

        if skin.get("stickers"):
            stickers_list = "\n".join(
                [f"— {sticker['name']}" for sticker in skin["stickers"]]
            )
            skin_text += f"\n🎟️ <b>Стикеры:</b>\n{stickers_list}"

        full_message += skin_text.strip()

        if idx < len(skins_to_send) - 1:
            full_message += "\n\n──────────────\n\n"

    await message.answer(full_message.strip(), parse_mode="HTML")


def check_item_against_conditions(
    item: dict, conditions: list[ConditionSchema]
) -> bool:
    item_name = item.get("name")
    item_float = item.get("item_float")
    item_pattern = str(item.get("item_paint_seed"))
    item_price = item.get("price")

    for cond in conditions:
        if cond.skin_name != item_name:
            continue

        if cond.float_condition:
            try:
                if ">" in cond.float_condition:
                    target_float = float(cond.float_condition.strip(" >"))
                    if not item_float or float(item_float) <= target_float:
                        continue

                elif "<" in cond.float_condition:
                    target_float = float(cond.float_condition.strip(" <"))
                    if not item_float or float(item_float) >= target_float:
                        continue

            except ValueError:
                logger.error(f"⚠️ Некорректное float_condition: {cond.float_condition}")
                continue

        if cond.patterns:
            if item_pattern not in cond.patterns:
                continue

        if cond.price_condition:
            try:
                if ">" in cond.price_condition:
                    target_price = float(cond.price_condition.strip(" >"))
                    if not item_price or float(item_price) <= target_price:
                        continue

                elif "<" in cond.price_condition:
                    target_price = float(cond.price_condition.strip(" <"))
                    if not item_price or float(item_price) >= target_price:
                        continue

            except ValueError:
                logger.error(f"⚠️ Некорректное price_condition: {cond.price_condition}")
                continue

        return True

    return False


def format_date(date_str: str) -> str:
    try:
        dt = datetime.fromisoformat(date_str.rstrip("Z"))
        return dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        return date_str


def format_item_message(item: dict, event: str) -> str:
    name = item.get("name", "Без названия")
    price = item.get("price", "?")
    unlock_at = format_date(item.get("unlock_at", "—"))
    created_at = format_date(item.get("created_at", "—"))
    float_value = item.get("item_float", "—")
    paint_seed = item.get("item_paint_seed", "—")

    title_map = {
        "obtained_skin_added": "💎 <b>Найден новый скин!</b>",
        "obtained_skin_price_changed": "💰 <b>Обновлена цена скина!</b>",
    }

    date_label = "Добавлен" if event == "obtained_skin_added" else "Обновлено"
    price_label = "Цена" if event == "obtained_skin_added" else "Новая цена"

    price_display = f"{price} $"
    try:
        price_float = float(price)
        price_rub = round(price_float * USD_TO_RUB)
        price_display = f"{price_float:.2f} $ ({price_rub} ₽)"

    except (ValueError, TypeError):
        pass

    return (
        f"{title_map.get(event, '')}\n\n"
        f"🎯 <b>{name}</b>\n"
        f"💰 {price_label}: <b>{price_display}</b>\n"
        f"🔓 Разблокировка: {unlock_at}\n"
        f"🕓 {date_label}: {created_at}\n"
        f"🧬 Флоат: {float_value}\n"
        f"🎨 Паттерн: {paint_seed}"
    )


def foramt_message(parsed_items: list[ParsedItems]) -> list[str]:
    messages = []
    current_chunk = ""

    for item in parsed_items:
        item_text = (
            f"🔹 <b>{item.skin_name}</b>\n"
            f"🧩 Паттерн: <code>{item.pattern or '—'}</code>\n"
            f"💧 Флоат: <code>{item.item_float or '—'}</code>\n"
            f"💰 Цена: <code>{item.price or '—'}</code>\n"
            f"🕒 Добавлено: <code>{item.created_at_lis.strftime('%Y-%m-%d %H:%M') if item.created_at_lis else '—'}</code>\n"
        )

        if item.unlock_at_lis:
            item_text += f"🔓 Разблокировка: <code>{item.unlock_at_lis.strftime('%Y-%m-%d %H:%M')}</code>\n"

        item_text += f"📅 Событие: <code>{item.event}</code>\n\n"

        if len(current_chunk) + len(item_text) > MAX_MESSAGE_LENGTH:
            messages.append(current_chunk.strip())
            current_chunk = item_text

        else:
            current_chunk += item_text

    if current_chunk:
        messages.append(current_chunk.strip())

    return messages
