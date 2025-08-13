from typing import Dict, List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

LINKS = [
    "https://eora.ru/cases/promyshlennaya-bezopasnost",
    "https://eora.ru/cases/lamoda-systema-segmentacii-i-poiska-po-pohozhey-odezhde",
    "https://eora.ru/cases/navyki-dlya-golosovyh-assistentov/karas-golosovoy-assistent",
    "https://eora.ru/cases/assistenty-dlya-gorodov",
    "https://eora.ru/cases/avtomatizaciya-v-promyshlennosti/chemrar-raspoznovanie-molekul",
    "https://eora.ru/cases/zeptolab-skazki-pro-amnyama-dlya-sberbox",
    "https://eora.ru/cases/goosegaming-algoritm-dlya-ocenki-igrokov",
    "https://eora.ru/cases/dodo-pizza-robot-analitik-otzyvov",
    "https://eora.ru/cases/ifarm-nejroset-dlya-ferm",
    "https://eora.ru/cases/zhivibezstraha-navyk-dlya-proverki-rodinok",
    "https://eora.ru/cases/sportrecs-nejroset-operator-sportivnyh-translyacij",
    "https://eora.ru/cases/avon-chat-bot-dlya-zhenshchin",
    "https://eora.ru/cases/navyki-dlya-golosovyh-assistentov/navyk-dlya-proverki-loterejnyh-biletov",
    "https://eora.ru/cases/computer-vision/iss-analiz-foto-avtomobilej",
    "https://eora.ru/cases/purina-master-bot",
    "https://eora.ru/cases/skinclub-algoritm-dlya-ocenki-veroyatnostej",
    "https://eora.ru/cases/skolkovo-chat-bot-dlya-startapov-i-investorov",
    "https://eora.ru/cases/purina-podbor-korma-dlya-sobaki",
    "https://eora.ru/cases/purina-navyk-viktorina",
    "https://eora.ru/cases/dodo-pizza-pilot-po-avtomatizacii-kontakt-centra",
    "https://eora.ru/cases/dodo-pizza-avtomatizaciya-kontakt-centra",
    "https://eora.ru/cases/icl-bot-sufler-dlya-kontakt-centra",
    "https://eora.ru/cases/s7-navyk-dlya-podbora-aviabiletov",
    "https://eora.ru/cases/workeat-whatsapp-bot",
    "https://eora.ru/cases/absolyut-strahovanie-navyk-dlya-raschyota-strahovki",
    "https://eora.ru/cases/kazanexpress-poisk-tovarov-po-foto",
    "https://eora.ru/cases/kazanexpress-sistema-rekomendacij-na-sajte",
    "https://eora.ru/cases/intels-proverka-logotipa-na-plagiat",
    "https://eora.ru/cases/karcher-viktorina-s-voprosami-pro-uborku",
    "https://eora.ru/cases/chat-boty/purina-friskies-chat-bot-na-sajte",
    "https://eora.ru/cases/nejroset-segmentaciya-video",
    "https://eora.ru/cases/chat-boty/essa-nejroset-dlya-generacii-rolikov",
    "https://eora.ru/cases/qiwi-poisk-anomalij",
]

BASE_URL = "https://eora.ru"

def parse_links(links: List[str]) -> List[Dict]:
    """
    Парсит список ссылок на документы или страницы.
    Для каждой ссылки скачивает и извлекает текст.
    Возращает список чанков с метаданными(url, текст).
    """
    chunks = []
    for url in links:
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                continue
            soup = BeautifulSoup(resp.text, "html.parser")
            main_text = " ".join([p.get_text() for p in soup.find_all("p")])
            if main_text.strip():
                chunks.append(
                    {
                        "source": url,
                        "text": main_text.strip(),
                        }
                    )
        except Exception as e:
            print(f"Ошибка анализа {url}: {e}.")
    return chunks

def crawl_site(
    base_url: str,
    max_pages=500,
) -> List[Dict]:
    """
    Рекурсивно парсит сайт, собирает текст со страниц.
    Возвращает список чанков с метаданными(url, текст).
    """
    visited = set()
    to_visit = [base_url]
    data = []

    for i, url in enumerate(to_visit):
        if i >= max_pages:
            break
        if url in visited:
            continue
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code != 200:
                continue
            soup = BeautifulSoup(resp.text, "html.parser")
            main_text = " ".join([p.get_text() for p in soup.find_all("p")])
            if main_text.strip():
                data.append(
                    {
                        "source":url,
                        "text": main_text.strip()
                        }
                    )
            for a in soup.find_all("a", href=True):
                if not isinstance(a, Tag):
                    continue
                href = a.get("href", None)
                if not isinstance(href, str):
                    continue
                link = urljoin(url, href)
                if link.startswith(base_url) and link not in visited and link not in to_visit:
                    to_visit.append(link)
            visited.add(url)
        except Exception as e:
            print(f"Ошибка анализа {url}: {e}.")
    return data


