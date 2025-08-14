import logging
import time
from typing import List

import numpy as np
import tiktoken

from app.config import MAX_TOKENS
from app.llm.openai.chunk import Chunk, split_text_by_tokens
from app.llm.openai.embeddings import OpenAIEmbeddingProvider
from app.scripts.chroma import get_chroma_client, get_or_create_collection


def index_chunks_in_chroma_openai(
    chunks: List[Chunk],
    collection_name: str = "eora_openai",
):
    """
    Индексирует чанки в ChromaDB для OpenAI.
    """
    logger = logging.getLogger(__name__)
    client = get_chroma_client()
    collection = _get_collection_or_raise(client, collection_name)
    enc = tiktoken.get_encoding("cl100k_base")

    texts, metadatas, ids = _prepare_chunks_for_indexing(chunks, enc, logger)
    _raise_if_no_texts(texts)
    texts, metadatas, ids = _final_filter_chunks(texts, metadatas, ids, enc, logger)
    _index_embeddings(collection, texts, metadatas, ids, logger)

def _get_collection_or_raise(client, collection_name):
    collection = get_or_create_collection(client, collection_name)
    if collection is None:
        raise RuntimeError(f"Не удалось получить или создать коллекцию ChromaDB с именем '{collection_name}'")
    return collection

def _raise_if_no_texts(texts):
    if not texts:
        raise ValueError("Нет непустых чанков для индексации!")

def _prepare_chunks_for_indexing(chunks, enc, logger):
    texts, metadatas, ids = [], [], []
    idx = 0
    for chunk in chunks:
        text = " ".join(chunk.content)
        if not text.strip():
            continue
        split_texts = split_text_by_tokens(text, enc, max_tokens=MAX_TOKENS)
        for part in split_texts:
            num_tokens = len(enc.encode(part))
            if num_tokens > MAX_TOKENS:
                logger.warning(f"Чанк превышает лимит: {num_tokens} токенов. Текст: {part[:100]}...")
                continue
            texts.append(part)
            metadatas.append({
                "source": str(chunk.source or ""),
                "title": str(chunk.title or "")
            })
            ids.append(str(idx))
            idx += 1
    return texts, metadatas, ids

def _final_filter_chunks(texts, metadatas, ids, enc, logger):
    filtered = []
    for t, m, i in zip(texts, metadatas, ids):
        num_tokens = len(enc.encode(t))
        if num_tokens > MAX_TOKENS or len(t) > 800:
            logger.error(f"CRITICAL: Чанк с {num_tokens} токенами и {len(t)} символами попал в эмбеддинги! Текст: {t[:100]}...")
            continue
        filtered.append((t, m, i))
    if len(filtered) < len(texts):
        logger.warning(f"Финально отфильтровано {len(texts) - len(filtered)} чанков, превышающих лимит токенов или длины перед эмбеддингами.")
    return map(list, zip(*filtered)) if filtered else ([], [], [])

def _index_embeddings(collection, texts, metadatas, ids, logger):
    embeddings = OpenAIEmbeddingProvider().embed(list(texts))
    logger.info(f"Эмбеддинги для OpenAI рассчитаны за {time.time() - time.time():.1f} сек.")
    if not embeddings:
        raise ValueError("Провайдер эмбеддингов вернул пустой список! Проверь ключи и лимиты.")
    if len(embeddings) != len(texts):
        logger.warning(f"{len(texts) - len(embeddings)} чанков не были проиндексированы из-за ошибки 413.")
        texts = texts[:len(embeddings)]
        metadatas = metadatas[:len(embeddings)]
        ids = ids[:len(embeddings)]
    embeddings_np = np.array(embeddings, dtype=np.float32)
    collection.add(
        embeddings=embeddings_np,
        documents=list(texts),
        metadatas=list(metadatas),
        ids=list(ids),
    )

def index_openai(chunks: List[Chunk]):
    index_chunks_in_chroma_openai(chunks, collection_name="eora_openai")