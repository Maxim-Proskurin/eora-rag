import os

from gigachat import GigaChat


def get_gigachat_access_token() -> str:
    """
    Получить access token GigaChat, используя Authorization Key из .env.
    """
    credentials = os.getenv("GIGACHAT_API_KEY")
    if not credentials:
        raise ValueError("GIGACHAT_API_KEY не найден в переменных окружения или .env")
    with GigaChat(credentials=credentials, verify_ssl_certs=False) as giga:
        _ = giga.chat("Проверь токен")
        access_token = giga._access_token
        if access_token is None:
            raise RuntimeError("Не удалось получить access token GigaChat")
        return str(access_token)