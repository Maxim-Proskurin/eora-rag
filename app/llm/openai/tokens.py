import os


def get_openai_api_key() -> str:
    """
    Получить OpenAI API ключ из переменных окружения или .env.
    """
    if api_key := os.getenv("OPENAI_API_KEY"):
        return api_key
    else:
        raise ValueError("OPENAI_API_KEY не найден в переменных окружения или .env")
