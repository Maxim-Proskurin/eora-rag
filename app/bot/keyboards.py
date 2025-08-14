"""
Клавиатуры и кнопки для Telegram-бота.
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_provider_keyboard():
    """
    Клавиатура для выбора провайдера эмбеддингов.
    """
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="GigaChat", callback_data="provider_gigachat"),
            InlineKeyboardButton(text="OpenAI", callback_data="provider_openai"),
        ]
    ])
    return kb