from typing import List

import openai

from app.config import BATCH_SIZE_OPENAI
from app.llm.openai.tokens import get_openai_api_key


class OpenAIEmbeddingProvider:
    """
    Провайдер эмбеддингов OpenAI.
    """
    def __init__(self):
        openai.api_key = get_openai_api_key()

    def embed(self, texts: List[str]) -> List[List[float]]:
        all_embeddings = []
        for i in range(0, len(texts), BATCH_SIZE_OPENAI):
            batch = texts[i:i+BATCH_SIZE_OPENAI]
            response = openai.embeddings.create(
                input=batch,
                model="text-embedding-3-small"
            )
            all_embeddings.extend([d.embedding for d in response.data])
        return all_embeddings