from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


skip_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="⏭ Skip")]],
    resize_keyboard=True,
    one_time_keyboard=True,
)
