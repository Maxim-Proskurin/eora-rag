# Тестовое задание на позицию Python-разработчик pre-Middle для компании EORA

## EORA RAG Service

Сервис для поиска и генерации ответов на вопросы по материалам компании EORA с помощью LLM (OpenAI) и Retrieval-Augmented Generation(RAG).

### Возможности

- Парсинг и индексация информации из списка ссылок и всего сайта eora.ru.
- Поиск релевантных фрагментов по вопросу пользователя.
- Генерация ответа с указанием источников (inline-ссылки).
- Современный стек: FastAPI, Poetry, ChromaDB, OpenAI, Pydantic, Docker.
- Автоматическое форматирование и линтинг кода (ruff, isort, pre-commit).

### Быстрый страрт

1. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/Maxim-Proskurin/eora-rag.git
   cd eora-rag

2. Установите зависимости:

   ```bash
   poetry install

3. Запустите приложение:

   ```bash
   poetry run python -m app.bot.run

4. Очистка базы ChromaDB(если требует):

   ```bash
   poetry run python -m app.scripts.reset_chroma

5. Проверка коллекции GigaChat:

   ```bash
   poetry run python -m app.scripts.gigachat.inspect_gigachat_collection

6. Проверка коллекции OpenAI:

   ```bash
   poetry run python -m app.scripts.openai.inspect_openai_collection

7. Индексация для GigaChat:

   ```bash
   poetry run python -m app.scripts.gigachat.index_gigachat

8. Индексация для OpenAI:

   ```bash
   poetry run python -m app.scripts.openai.index_openai

9. Генерация FAQ-ответов для GigaChat:

   ```bash
   poetry run python -m app.scripts.gigachat.save_answer_gigachat

10. Генерация FAQ-ответов для OpenAI:

    ```bash
    poetry run python -m app.scripts.openai.save_answer_openai


### Структура проекта

- app/bot - Логика бота(кнопки, сообщения и тд.).
- app/data - Парсер, ссылки
- app/llm/gigachat - Все что связано для взаимодействия с gigachat(ом)(индексы, эмбеддинги, ответы, промты(будут завтра), чанки и тд.).
- app/llm/openai - Все что связано с взаимодействием с gpt (индексы, эмбеддинги, ответы, промты(будут завтра), чанки и тд.).
- app/script - Так же разбиты на части openai/gigachat(индексация, частые вопросы, просмотр коллекции, а так же быстрая проверка/очистка db).

### Современные практики

- Poetry для управления зависимостями.
- Pydantic BaseSettings для конфигов.(лучше dotenv ничего не нашел).
- pre-commit(ruff, isort) для чистоты кода.

### TODO(минимальный)

- [x] Реализовать парсинг и индексацию всех источников.
- [x] Интегрировать Chromadb и OpenAI.
- [] Добавить эндпоинты FastAPI.
- [] Покрыть тестами.

### Прогресс (актуально на текущий этап)

- [x] Реализован парсинг ссылок и сайта, сбор всех чанков (`app/data.py`, `app/rag.py`).
- [x] Централизованная работа с токенами OpenAI и GigaChat (`app/llm_tokens.py`).
- [x] Функция получения эмбеддингов для OpenAI и GigaChat (`app/rag.py`).
- [x] Интеграция с ChromaDB: индексация и поиск по эмбеддингам.
- [x] Генерация ответа с использованием найденных чанков (RAG).
- [ ] FastAPI endpoint для вопросов/ответов.
- [ ] Покрытие тестами (unit/integration).
- [x] Оформить обработку ошибок и логирование.

### Что произошло интересного

- Переписал два раза полностью архитектуру(if на if на if дело сомнительно(зато с тестами проблем будет гораздо меньше)).
- Понял что слизывать мы так и не научились.
- Промты оказывается реально сложная штука.
- Понял что визуально на данном этапе проще сделать бота в тг чем через тот же swagger пытаться(но в ближайшее время реализую).
