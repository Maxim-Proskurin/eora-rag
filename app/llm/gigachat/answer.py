import os
import re
from typing import Optional

from gigachat import GigaChat

from app.llm.gigachat.search import query_chroma_gigachat


def generate_answer_gigachat(
    question: str,
    collection_name: str,
    n_results: int = 50,
    history: Optional[list[str]] = None,
) -> str:
    """
    Генерирует ответ на вопрос на основе чанков и GigaChat.
    """
    results = query_chroma_gigachat(
        query=question,
        collection_name=collection_name,
        n_results=n_results,
    )
    docs = (results.get("documents") or [[]])[0]
    metadatas = (results.get("metadatas") or [[]])[0]

    # Логирование топ-чанков для отладки.
    print("Топ чанки для ответа:")
    for i, (doc, meta) in enumerate(zip(docs, metadatas), 1):
        print(f"[{i}] {meta.get('source', '')}: {doc[:100]}...")

    context = ""
    sources = []
    for i, (doc, meta) in enumerate(zip(docs, metadatas), 1):
        url = meta.get('case_url') or meta.get('url') or meta.get('source', '')
        context += f"[{i}] {doc}\n"
        sources.append(f"[{i}] {url}")

    if not docs:
        return "Нет релевантных источников для ответа на ваш вопрос."

    history_block = ""
    if history:
        history_block = (
            "Ранее пользователь уже спрашивал:\n"
            + "\n".join(f"- {q}" for q in history if q.strip())
            + "\nПостарайся не повторять предыдущие ответы, а привести новые примеры или переформулировать ответ.\n"
        )

    prompt = (
    "Вот выдержки из разных проектов сайта eora.ru:\n"
    f"{context}\n"
    "Перечисли только конкретные найденные факты, связанные с вопросом пользователя, и укажи ссылки на источники.\n"
    "Строго придерживайся структуры: каждый пункт - отдельный факт, не объединяй разные кейсы в один пункт, не меняй стиль ответа между запросами.\n"
    "Не делай выводов, не пиши вступлений и заключений, не обобщай. Только список фактов и ссылки.\n"
    f"{history_block}"
    f"Вопрос: {question}\n"
    "Если нет информации, честно напиши, что ничего не найдено."
)

    with GigaChat(credentials=os.getenv("GIGACHAT_API_KEY"), verify_ssl_certs=False) as giga:
        llm_answer = giga.chat(prompt)
        answer_text = llm_answer.choices[0].message.content if hasattr(llm_answer, "choices") else str(llm_answer)

    def linkify_answer(answer_text, sources):
        url_map = {}
        for s in sources:
            match = re.match(r"\[(\d+)\]\s*(.*)", s)
            if match:
                idx = match[1]
                url = match[2].strip()
                url_map[idx] = url
        def repl(m):
            idx = m.group(1)
            url = url_map.get(idx)
            return f'<a href="{url}">[{idx}]</a>' if url else f"[{idx}]"
        text = re.sub(r"\[(\d+)\]", repl, answer_text)
        text = re.sub(r"^#+\s*\*\*(.+?)\*\*", r"\1", text, flags=re.MULTILINE)
        text = re.sub(r"^#+\s*(.+)", r"\1", text, flags=re.MULTILINE)
        text = re.sub(r"\n{3,}", r"\n\n", text)
        return text

    answer_text_linked = linkify_answer(answer_text, sources)

    # Собираем уникальные источники для блока "Источники" в нужном формате.
    unique_sources = {}
    used_indices = set(re.findall(r"\[(\d+)\]", answer_text_linked))
    for s in sources:
        match = re.match(r"\[(\d+)\]\s*(.*)", s)
        if match:
            idx = match[1]
            url = match[2].strip()
            if idx not in used_indices:
                continue
            if not url or "review" in url or url.endswith("#") or url.endswith("/#"):
                continue
            unique_sources[idx] = url

    # Перенумеровываем источники: [1], [2], ... и заменяем индексы в ответе.
    idx_map = {old_idx: str(new_idx) for new_idx, old_idx in enumerate(sorted(unique_sources.keys(), key=int), 1)}
    def renumber_links(m):
        old_idx = m.group(1)
        return f"[{idx_map[old_idx]}]" if old_idx in idx_map else ""
    answer_text_linked = re.sub(r"\[(\d+)\]", renumber_links, answer_text_linked)
    if unique_sources:
        sources_block = "Источники:\n" + "\n".join(f"[{idx_map[old_idx]}] {unique_sources[old_idx]}" for old_idx in sorted(unique_sources.keys(), key=int))
    else:
        sources_block = ""

    answer_text_linked = re.sub(r"\*\*(.+?)\*\*", r"\1", answer_text_linked)
    answer_text_linked = re.sub(r"^(\s*)>\s?", r"\1- ", answer_text_linked, flags=re.MULTILINE)

    return f"Вопрос: {question}\n\nОтвет:\n{answer_text_linked}\n\n{sources_block}\n\nЕсли у вас есть ещё вопросы - напишите, я помогу!"