from typing import Any, Dict

import numpy as np

from app.llm.openai.embeddings import OpenAIEmbeddingProvider
from app.scripts.chroma import get_chroma_client, get_or_create_collection


def query_chroma_openai(
    query: str,
    collection_name: str = "eora_openai",
    n_results: int = 50,
) -> Dict[str, Any]:
    """
    Выполняет поиск по ChromaDB по эмбеддингу запроса (OpenAI).

    :param query: Вопрос пользователя (строка).
    :param collection_name: Имя коллекции ChromaDB.
    :param n_results: Сколько результатов вернуть.
    :return: Словарь с документами, метаданными и расстояниями.
    """
    client = get_chroma_client()
    collection = get_or_create_collection(client, collection_name)
    if collection is None:
        raise RuntimeError(f"Не удалось получить или создать коллекцию ChromaDB с именем '{collection_name}'")
    query_emb = OpenAIEmbeddingProvider().embed([query])[0]
    results = collection.query(
        query_embeddings=np.array([query_emb], dtype=np.float32),
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )
    return dict(results)