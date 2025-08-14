import base64
import os
from typing import List

import tiktoken
from gigachat import GigaChat

from app.config import BATCH_SIZE_GIGACHAT, MAX_TOKENS


class GigaChatEmbeddingProvider:
    """
    Провайдер эмбеддингов GigaChat.
    """
    def __init__(self):
        self.enc = tiktoken.get_encoding("cl100k_base")
        self.credentials = os.getenv("GIGACHAT_API_KEY")
        if not self.credentials:
            raise ValueError("GIGACHAT_API_KEY не найден в переменных окружения или .env")
        try:
            decoded = base64.b64decode(self.credentials).decode("utf-8")
            if ":" not in decoded:
                raise ValueError
        except Exception:
            raise RuntimeError("GIGACHAT_API_KEY должен быть корректным base64 от строки client_id:client_secret. Проверь .env!")

    def embed(self, texts: List[str]) -> List[List[float]]:
        import logging
        logger = logging.getLogger(__name__)
        texts = [t for t in texts if len(self.enc.encode(t)) <= MAX_TOKENS]
        all_embeddings = []
        with GigaChat(credentials=self.credentials, verify_ssl_certs=False) as giga:
            for i in range(0, len(texts), BATCH_SIZE_GIGACHAT):
                batch = texts[i:i+BATCH_SIZE_GIGACHAT]
                try:
                    embeddings_obj = giga.embeddings(batch)
                    if hasattr(embeddings_obj, "data"):
                        all_embeddings.extend([emb.embedding for emb in embeddings_obj.data])
                except Exception as e:
                    logger.warning(f"GigaChat batch error: {e}, falling back to single embedding.")
                    for t in batch:
                        try:
                            embeddings_obj = giga.embeddings([t])
                            if hasattr(embeddings_obj, "data"):
                                all_embeddings.extend([emb.embedding for emb in embeddings_obj.data])
                        except Exception as e:
                            logger.error(f"GigaChat single embedding error: {e}")
        return all_embeddings