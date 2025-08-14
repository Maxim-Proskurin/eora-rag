import os
import re
from typing import Optional

import openai
from dotenv import load_dotenv

from app.llm.openai.search import query_chroma_openai

load_dotenv()

def generate_answer_openai(
    question: str,
    collection_name: str,
    n_results: int = 50,
    history: Optional[list[str]] = None,
) -> str:
    """
    Генерирует ответ на вопрос на основе чанков и OpenAI GPT.
    """
    results = query_chroma_openai(
        query=question,
        collection_name=collection_name,
        n_results=n_results,
    )
    docs = (results.get("documents") or [[]])[0]
    metadatas = (results.get("metadatas") or [[]])[0]

    # Логирование  для отладки.
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

    max_context_chars = 7000
    prompt = (
    "Вот выдержки из разных проектов сайта eora.ru:\n"
    f"{context[:max_context_chars]}\n"
    "Выдели 5 самых передовых или интересных кейсов для ритейлеров. Для каждого пункта:\n"
    "- Укажи компанию или организацию, для которой реализован проект (если есть в тексте).\n"
    "- Кратко (3-4 строки) опиши, какую задачу или проблему решал проект, и почему он интересен.\n"
    "- После описания каждого кейса поставь активную ссылку в формате <a href=\"ссылка\">[N]</a>, где N - номер пункта, а ссылка - url проекта. Ссылка [N] должна вести именно на тот кейс, который описан в этом пункте. Не пиши слово 'url'!\n"
    "- Между пунктами делай пустую строку для удобства чтения.\n"
    "- Начинай список с наиболее известных компаний (например, Магнит, KazanExpress, Dodo Pizza, Purina, WorkEat, ZeptoLab, S7, Karcher, Skolkovo, QIWI, Sber и т.д.), если такие есть в выдержках.\n"
    "Если вопрос не про кейсы, а про технологии, подходы, интеграции, автоматизацию, расскажи кратко (1-2 абзаца) о возможностях компании, с примерами из выдержек и ссылками на кейсы.\n"
    "Если вопрос содержит нецензурную брань или ругательства, ответь с лёгкой ироничной шуткой, например: 'Ой, давайте без ругательств - у нас тут искусственный интеллект, а не искусственный хам!' и не выдавай никакой информации по сути вопроса.\n"
    "Формат ответа:\n"
    "{question}\n"
    "\n"
    "Мы разработали для <компания> <краткое описание задачи/решения>. <a href=\"ссылка1\">[1]</a>\n"
    "\n"
    "Для <компания> создали <краткое описание>. <a href=\"ссылка2\">[2]</a>\n"
    "\n"
    "...\n"
    "Не делай выводов, не пиши вступлений и заключений, не обобщай. Только структурированный список фактов и ссылки.\n"
    "Если нет информации, честно напиши, что ничего не найдено."
)
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
        max_tokens=1024,
    )
    answer_text = response.choices[0].message.content

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
            # Не делаем ссылку, если url пустой.
            if not url or url in ("-", "#") or url.startswith("http") is False:
                return f"[{idx}]"
            return f'<a href="{url}">[{idx}]</a>'
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
            if not url or "review" in url or url.endswith("#") or url.endswith("/#") or url in ("-",):
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