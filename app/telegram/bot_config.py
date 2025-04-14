from aiogram import Bot

from app.config import settings

bot = Bot(token=settings.TELEGRAM.token)
