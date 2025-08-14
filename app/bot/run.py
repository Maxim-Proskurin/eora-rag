"""
Точка входа для Telegram-бота EORA RAG.
"""

import os

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from app.bot.handlers import provider_handler, question_handler, start_handler

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def main():
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN не найден в переменных окружения или .env")

    bot = Bot(
        token=TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Регистрация хендлеров
    dp.message.register(start_handler, Command("start"))
    dp.callback_query.register(provider_handler, F.data.startswith("provider_"))
    dp.message.register(question_handler)

    print("Бот запущен!")
    dp.run_polling(bot)

if __name__ == "__main__":
    main()