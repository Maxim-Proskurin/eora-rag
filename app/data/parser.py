"""
Парсер сайта и ссылок для получения чанков.
"""

from typing import Dict, List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag


def parse_links(links: List[str]) -> List[Dict]:
    """
    Скачивает каждую страницу из списка ссылок,
    извлекает текст и возвращает список чанков с метаданными.
    """
    chunks = []
    for url in links:
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                continue
            soup = BeautifulSoup(resp.text, "html.parser")
            current_chunk = {"title": None, "content": [], "source": url}
            for el in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'div']):
                if isinstance(el, Tag):
                    if el.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        if current_chunk["title"] or current_chunk["content"]:
                            chunks.append(current_chunk)
                        current_chunk = {"title": el.text.strip(), "content": [], "source": url}
                    elif el.name in ['p', 'li']:
                        current_chunk["content"].append(el.text.strip())
                    elif el.name == 'div':
                        if text := el.get_text(strip=True):
                            current_chunk["content"].append(text)
            if current_chunk["title"] or current_chunk["content"]:
                content_text = " ".join(current_chunk["content"]).strip()
                title_text = current_chunk["title"] or ""
                if content_text and content_text.lower() != title_text.lower():
                    chunks.append(current_chunk)
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Ошибка анализа {url}: {e}.")
    return chunks

def crawl_site(
    base_url: str,
    max_pages: int = 50,
) -> List[Dict]:
    """
    Рекурсивно парсит сайт, собирает текст со страниц.
    Возвращает список чанков с метаданными (url, текст).
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
            current_chunk = {"title": None, "content": [], "source": url}
            for el in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'div']):
                if isinstance(el, Tag):
                    if el.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        if current_chunk["title"] or current_chunk["content"]:
                            data.append(current_chunk)
                        current_chunk = {"title": el.text.strip(), "content": [], "source": url}
                    elif el.name in ['p', 'li']:
                        current_chunk["content"].append(el.text.strip())
                    elif el.name == 'div':
                        if text := el.get_text(strip=True):
                            current_chunk["content"].append(text)
            if current_chunk["title"] or current_chunk["content"]:
                content_text = " ".join(current_chunk["content"]).strip()
                title_text = current_chunk["title"] or ""
                if content_text and content_text.lower() != title_text.lower():
                    data.append(current_chunk)

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
            import logging
            logging.getLogger(__name__).warning(f"Ошибка анализа {url}: {e}.")
    return data