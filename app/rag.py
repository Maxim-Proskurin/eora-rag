from app.data import BASE_URL, LINKS, crawl_site, parse_links

from.llm_tokens import get_openai_api_key
import os
from typing import Dict, List

import openai
from dotenv import load_dotenv
from gigachat import GigaChat

load_dotenv()

def get_all_chunks() -> List[Dict]:
    """
    Получить все чанки из ссылок с сайта.
    """
    link_chunks = parse_links(LINKS)
    site_chunks = crawl_site(BASE_URL, max_pages=50)
    return link_chunks + site_chunks

def embed_texts(
    texts: List[str],
    provider: str = "openai",
) -> List[List[float]]:
    """
    Получить эмбеддинги для списка текстов через OpenAI или GigaChat.
    provider: "openai" либо "gigachat".
    """
    if provider == "openai":
        openai.api_key = get_openai_api_key()
        response = openai.embeddings.create(
            input=texts,
            model="text-embedding-3-small"
        )
        return [d.embedding for d in response.data]
    elif provider == "gigachat":
        credentials = os.getenv("GIGACHAT_API_KEY")
        if not credentials:
            raise ValueError("GIGACHAT_API_KEY не найден в переменных окружения или .env")
        with GigaChat(credentials=credentials, verify_ssl_certs=False) as giga:
            embeddings_obj = giga.embeddings(texts)
            if hasattr(embeddings_obj, "data"):
                return [emb.embedding for emb in embeddings_obj.data]
            else:
                raise TypeError("Не удалось получить список эмбеддингов из ответа GigaChat")
    else:
        raise ValueError(f"Неизвестный провайдер: {provider}")