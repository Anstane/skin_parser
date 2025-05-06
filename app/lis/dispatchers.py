import json

from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.telegram.buttons import (
    skip_keyboard,
    yes_no_kb,
    parse_action_kb,
    start_parse_kb,
)

from app.lis.states import AuthStates, SearchForSkinStates, ParseStates
from app.lis.constants import SKIN_NAME_INPUT_PROMPT, JSON_SEARCH_PROMPT
from app.lis.service import get_user_balance, send_request_for_skins
from app.lis.factory import handle_start_parse
from app.lis.utils import send_first_skins
from app.lis import crud as lis_crud

dp = Dispatcher()


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

    await send_first_skins(message=message, skins=skins)


@dp.message(Command("lis_parse"))
async def lis_parse(message: Message, state: FSMContext) -> None:
    tg_id = message.from_user.id

    user_exists = await lis_crud.check_exist_user_or_not(tg_id=tg_id)

    if not user_exists:
        await message.answer(
            "🔒 Вы ещё не авторизованы. Используйте команду /lis_auth."
        )
        return

    active_parse_model = await lis_crud.get_user_parse_model(tg_id=tg_id)

    if active_parse_model:
        if active_parse_model.is_active:
            await message.answer(
                "🟢 Парс уже активен. Хотите добавить предметы или остановить парсинг?",
                reply_markup=parse_action_kb,
            )
            await state.set_state(ParseStates.active_parse_action)
            return

        else:
            existed_items = await lis_crud.get_items_by_tg_id(tg_id=tg_id)

            if existed_items:
                item_list = "\n".join(f"• {item.skin_name}" for item in existed_items)
                await message.answer(
                    "⛔️ Парс в данный момент неактивен.\n\n"
                    f"🔎 У вас уже добавлены предметы для парса:\n\n{item_list}\n\n"
                    "Что вы хотите сделать?",
                    reply_markup=start_parse_kb,
                )
                await state.set_state(ParseStates.confirm_start_parse)
                return

    await message.answer(
        "Хотите начать парсинг предметов?",
        reply_markup=yes_no_kb,
    )
    await state.set_state(ParseStates.ask_to_start_first_parse)


@dp.message(ParseStates.ask_to_start_first_parse)
async def on_first_parse_start(message: Message, state: FSMContext):
    text = message.text.strip()

    if text == "✅ Да":
        await message.answer("🔍 Введите название предмета, который вы хотите парсить:")
        await state.set_state(ParseStates.add_item_name)

    elif text == "❌ Нет":
        await message.answer("❌ Отменено.")
        await state.clear()


@dp.message(ParseStates.add_item_name)
async def on_item_name(message: Message, state: FSMContext):
    skin_name = message.text.strip()

    await state.update_data(skin_name=skin_name)

    await message.answer(
        "🎯 Укажите float (например: `>0.15`, `<0.05`, или оставьте пустым):"
    )

    await state.set_state(ParseStates.add_item_float)


@dp.message(ParseStates.add_item_float)
async def on_item_float(message: Message, state: FSMContext):
    float_input = message.text.strip()

    await state.update_data(float=float_input if float_input else None)

    await message.answer(
        "🎨 Введите список паттернов (через запятую), или оставьте пустым:"
    )

    await state.set_state(ParseStates.add_item_patterns)


@dp.message(ParseStates.add_item_patterns)
async def on_item_patterns(message: Message, state: FSMContext):
    patterns_input = message.text.strip()

    patterns = (
        [p.strip() for p in patterns_input.split(",") if p.strip()]
        if patterns_input
        else []
    )

    data = await state.get_data()

    await lis_crud.add_item_to_parse(
        tg_id=message.from_user.id,
        skin_name=data["skin_name"],
        float=data["float"],
        patterns=patterns,
    )

    await message.answer(
        "✅ Предмет добавлен. Хотите добавить ещё один?", reply_markup=yes_no_kb
    )

    await state.set_state(ParseStates.confirm_add_another)


@dp.message(ParseStates.confirm_add_another)
async def on_confirm_add_another(message: Message, state: FSMContext):
    text = message.text.strip()
    tg_id = message.from_user.id

    if text == "✅ Да":
        await message.answer("🔍 Введите название следующего предмета:")
        await state.set_state(ParseStates.add_item_name)

    elif text == "❌ Нет":
        await message.answer("⚡️ Начинаем парсинг...")

        tg_id = message.from_user.id

        await handle_start_parse(tg_id=tg_id)
