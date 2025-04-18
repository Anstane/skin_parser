from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app.lis.service import get_user_balance
from app.lis import crud as lis_crud

dp = Dispatcher()


class AuthStates(StatesGroup):
    waiting_for_token = State()


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
