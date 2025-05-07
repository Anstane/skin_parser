from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


skip_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="⏭ Skip")]],
    resize_keyboard=True,
    one_time_keyboard=True,
)


yes_no_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="✅ Да"),
            KeyboardButton(text="❌ Нет"),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)


parse_action_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="➕ Добавить предметы"),
            KeyboardButton(text="🗑 Удалить предметы"),
        ],
        [KeyboardButton(text="🛑 Остановить парс")],
        [KeyboardButton(text="❌ Ничего")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)


start_parse_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Возобновить")],
        [
            KeyboardButton(text="➕ Добавить предметы"),
            KeyboardButton(text="🗑 Удалить предметы"),
        ],
        [KeyboardButton(text="❌ Ничего")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)
