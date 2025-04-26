import json

from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app.telegram.buttons import skip_keyboard
from app.telegram.constants import SKIN_NAME_INPUT_PROMPT, JSON_SEARCH_PROMPT

from app.lis.service import get_user_balance, send_request_for_skins
from app.lis import crud as lis_crud

dp = Dispatcher()

MAX_MESSAGE_LENGTH = 4096


class AuthStates(StatesGroup):
    waiting_for_token = State()


class SearchForSkinStates(StatesGroup):
    lis_token = State()
    waiting_for_skin_name = State()
    waiting_for_optional_search_params = State()


@dp.message(Command("lis_auth"))
async def handle_lis_auth(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id

    user_exists = await lis_crud.check_exist_user_or_not(tg_id=user_id)

    if user_exists:
        await message.answer("✅ Вы уже зарегистрированы.")

    else:
        await message.answer("🔑 Отправьте, пожалуйста, ваш LIS токен.")

        await state.set_state(AuthStates.waiting_for_token)


@dp.message(AuthStates.waiting_for_token)
async def process_token(message: Message, state: FSMContext) -> None:
    token = message.text
    user_id = message.from_user.id

    auth_model = await lis_crud.add_lis_auth(user_id=user_id, token=token)

    if auth_model:
        await message.answer("✅ Вы успешно зарегистрированы.")

    else:
        await message.answer("❌ Произошла ошибка в ходе регистрации!")

    await state.clear()


@dp.message(Command("lis_balance"))
async def check_lis_balance(message: Message) -> None:
    user_id = message.from_user.id

    user_exists = await lis_crud.check_exist_user_or_not(tg_id=user_id)

    if user_exists:
        balance_data = await get_user_balance(lis_token=user_exists.lis_token)

        if "balance" in balance_data:
            balance = balance_data["balance"]
            await message.answer(f"💰 Ваш баланс: {balance}")

        else:
            await message.answer("❌ Не удалось получить баланс. Попробуйте позже.")

    else:
        await message.answer(
            "🔒 Вы ещё не авторизованы. Используйте команду /lis_auth."
        )


@dp.message(Command("lis_search"))
async def get_skins_available_for_purchase(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    user_exists = await lis_crud.check_exist_user_or_not(tg_id=user_id)

    if user_exists:
        await state.update_data(lis_token=user_exists.lis_token)

        await message.answer(
            SKIN_NAME_INPUT_PROMPT,
            reply_markup=skip_keyboard,
            parse_mode="HTML",
        )

        await state.set_state(SearchForSkinStates.waiting_for_skin_name)

    else:
        await message.answer(
            "🔒 Вы ещё не авторизованы. Используйте команду /lis_auth."
        )


@dp.message(SearchForSkinStates.waiting_for_skin_name)
async def get_skin_name(message: Message, state: FSMContext) -> None:
    skin_name = message.text.strip()

    if skin_name.lower() in {"skip", "⏭ skip", "⏭️", "⏭"}:
        await state.update_data(names=[])

    elif skin_name:
        await state.update_data(names=[skin_name])

    else:
        await message.answer(
            "❗ Пожалуйста, введите корректное название скина или нажмите кнопку ⏭ Skip.",
            reply_markup=skip_keyboard,
        )
        return

    await message.answer(
        "🔍 Название получено!\n\n"
        "Теперь вы можете указать <b>дополнительные параметры поиска</b> в формате JSON, "
        "или нажмите кнопку ⏭ <b>Skip</b>, чтобы пропустить этот шаг.\n\n"
        f"{JSON_SEARCH_PROMPT}",
        reply_markup=skip_keyboard,
        parse_mode="HTML",
    )

    await state.set_state(SearchForSkinStates.waiting_for_optional_search_params)


@dp.message(SearchForSkinStates.waiting_for_optional_search_params)
async def get_optional_params_and_search(message: Message, state: FSMContext) -> None:
    user_input = message.text.strip()

    allowed_keys = {
        "float_from": float,
        "float_to": float,
        "only_unlocked": int,
        "price_from": (int, float),
        "price_to": (int, float),
        "sort_by": str,
    }

    allowed_sort_values = {"oldest", "newest", "lowest_price", "highest_price"}

    if user_input.lower() in {"skip", "⏭ skip", "⏭"}:
        optional_params = {}

    else:
        try:
            optional_params = json.loads(user_input)

            if not isinstance(optional_params, dict):
                raise ValueError("JSON is not a dictionary.")

            for key, value in optional_params.items():
                if key not in allowed_keys:
                    await message.answer(
                        f"❗ Недопустимый параметр: <code>{key}</code>",
                        parse_mode="HTML",
                    )
                    return

                expected_type = allowed_keys[key]
                if not isinstance(value, expected_type):
                    await message.answer(
                        f"❗ Неверный тип для <code>{key}</code>. "
                        f"Ожидался тип <b>{expected_type.__name__ if isinstance(expected_type, type) else '/'.join(t.__name__ for t in expected_type)}</b>.",
                        parse_mode="HTML",
                    )
                    return

                if key == "sort_by" and value not in allowed_sort_values:
                    await message.answer(
                        "❗ Недопустимое значение для <code>sort_by</code>.\n"
                        "Возможные значения: "
                        "<code>oldest</code>, <code>newest</code>, <code>lowest_price</code>, <code>highest_price</code>",
                        parse_mode="HTML",
                    )
                    return

        except Exception as e:
            await message.answer(
                "❗ Неверный формат JSON.\nПожалуйста, отправьте корректный JSON или нажмите ⏭ Skip.",
                parse_mode="HTML",
            )
            return

    data = await state.get_data()
    names = data.get("names", [])
    lis_token = data.get("lis_token")

    request_body = {
        **optional_params,
    }
    if names:
        request_body["names[]"] = names

    await message.answer(
        f"📤 Отправляем запрос с параметрами:\n<pre>{json.dumps(request_body, indent=2, ensure_ascii=False)}</pre>",
        parse_mode="HTML",
    )

    await state.clear()

    response = await send_request_for_skins(data=request_body, lis_token=lis_token)

    skins = response.get("data", [])

    if not skins:
        await message.answer("❌ Скины не найдены по заданным параметрам.")
        return

    await send_first_skins(message, skins)


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
