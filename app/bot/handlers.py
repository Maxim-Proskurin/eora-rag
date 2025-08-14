"""
Хендлеры Telegram-бота.
"""

import re

from aiogram import types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from app.bot.keyboards import get_provider_keyboard
from app.llm.gigachat.answer import generate_answer_gigachat
from app.llm.openai.answer import generate_answer_openai


def escape_markdown(text: str) -> str:
    # Экранирует спецсимволы MarkdownV2
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)

async def start_handler(message: types.Message):
    """
    Обработка команды /start.
    """
    welcome_text = (
        "👋 Привет! Я бот для тестового задания для EORA.\n\n"
        "Я могу ответить на вопросы по проектам и кейсам компании EORA, используя только информацию с сайта eora.ru.\n\n"
        "Пожалуйста, выберите провайдера:"
    )
    await message.answer(welcome_text, reply_markup=get_provider_keyboard())

async def provider_handler(callback_query: types.CallbackQuery, state):
    """
    Обработка выбора провайдера.
    """
    data = callback_query.data or ""
    provider = data.split("_", 1)[1] if "_" in data else "gigachat"
    await state.update_data(provider=provider)
    if callback_query.message:
        await callback_query.message.answer("Введите ваш вопрос:")

def get_stop_keyboard():
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Завершить диалог")]],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return kb

async def question_handler(message: types.Message, state):
    data = await state.get_data()
    provider = data.get("provider", "gigachat")
    question = message.text or ""
    if question.lower() in ("завершить", "стоп", "выход", "завершить диалог", "/stop"):
        await message.answer("Спасибо за вопросы! Если что - просто напишите /start.", reply_markup=types.ReplyKeyboardRemove())
        await state.clear()
        return
    collection_name = f"eora_{provider}"
    if provider == "gigachat":
        answer = generate_answer_gigachat(question, collection_name=collection_name)
    elif provider == "openai":
        answer = generate_answer_openai(question, collection_name=collection_name)
    else:
        answer = "Неизвестный провайдер."
    await message.answer(answer[:4000], parse_mode="HTML", reply_markup=get_stop_keyboard())
    await message.answer("Можете задать следующий вопрос или нажмите 'Завершить диалог'.", reply_markup=get_stop_keyboard())
