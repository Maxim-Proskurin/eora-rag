import re
import string
from dataclasses import dataclass
from typing import List, Optional

from app.data.parser import crawl_site, parse_links
from app.data.sources import BASE_URL, LINKS


@dataclass
class Chunk:
    """
    Единица информации для индексации и поиска.
    """
    title: Optional[str]
    content: List[str]
    source: str

def is_meaningful_chunk(text: str) -> bool:
    if not text:
        return False
    letters = sum(bool(c.isalpha()) for c in text)
    if letters / max(len(text), 1) < 0.3:
        return False
    words = set(text.split())
    if len(words) < 5:
        return False
    if text.strip().startswith("{") and text.strip().endswith("}"):
        return False
    if (sum(c in string.punctuation for c in text) / max(len(text), 1)) > 0.5:
        return False
    # Жёсткая фильтрация по json.
    bad_patterns = [
        "li_nm", "li_type", "li_ph", "lid", "ls", "loff", "li_parent_id",
        "корректный e-mail", "корректное имя", "корректный номер телефона",
        "Пожалуйста, введите", "Обязательное поле", "Слишком короткое значение"
    ]
    bad_count = sum(text.count(pat) for pat in bad_patterns)
    return bad_count == 0

def split_text_by_tokens(text: str, enc, max_tokens: int = 300, min_chars: int = 1) -> List[str]:
    """
    Разбивает текст на чанки по предложениям и лимиту токенов.
    Гарантирует, что ни один чанк не превышает max_tokens.
    Если не удаётся разбить по предложениям, нарезает по токенам.
    """
    def clean_text(text: str) -> str:
        text = re.sub(r"<[^>]+>", "", text)
        return re.sub(r"\s+", " ", text).strip()

    def split_sentences(text: str) -> List[str]:
        return re.split(r'(?<=[.!?])\s+', text)

    def add_chunk_if_meaningful(parts: list, chunk: str, min_chars: int):
        if chunk and len(chunk) >= min_chars:
            parts.append(chunk)

    text = clean_text(text)
    sentences = split_sentences(text)
    parts = []
    current_part = ""
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        sentence_tokens = enc.encode(sentence)
        while len(sentence_tokens) > max_tokens:
            part_tokens = sentence_tokens[:max_tokens]
            part_text = enc.decode(part_tokens)
            add_chunk_if_meaningful(parts, current_part, min_chars)
            current_part = ""
            parts.append(part_text)
            sentence_tokens = sentence_tokens[max_tokens:]
        if sentence_tokens:
            sentence = enc.decode(sentence_tokens)
            current_tokens = enc.encode(current_part) if current_part else []
            if len(current_tokens) + len(sentence_tokens) <= max_tokens:
                current_part = f"{current_part} {sentence}".strip() if current_part else sentence
            else:
                add_chunk_if_meaningful(parts, current_part, min_chars)
                current_part = sentence
    if current_part and len(current_part) >= min_chars:
        current_tokens = enc.encode(current_part)
        while len(current_tokens) > max_tokens:
            part_tokens = current_tokens[:max_tokens]
            part_text = enc.decode(part_tokens)
            parts.append(part_text)
            current_tokens = current_tokens[max_tokens:]
        if current_tokens:
            part_text = enc.decode(current_tokens)
            if len(part_text) >= min_chars:
                parts.append(part_text)

    def split_and_filter_long_chunks(parts: list) -> list:
        final_parts = []
        for part in parts:
            tokens = enc.encode(part)
            if len(tokens) > max_tokens:
                for i in range(0, len(tokens), max_tokens):
                    chunk_tokens = tokens[i:i+max_tokens]
                    chunk_text = enc.decode(chunk_tokens)
                    if len(chunk_text) >= min_chars and is_meaningful_chunk(chunk_text):
                        final_parts.append(chunk_text)
            elif is_meaningful_chunk(part):
                final_parts.append(part)
        return final_parts

    return split_and_filter_long_chunks(parts)

def get_all_chunks() -> List[Chunk]:
    """
    Собирает все чанки с сайта и по ссылкам.
    """
    dict_chunks = parse_links(LINKS) + crawl_site(BASE_URL, max_pages=1)
    return [Chunk(**chunk) for chunk in dict_chunks]