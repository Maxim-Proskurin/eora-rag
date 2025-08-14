import json

from dotenv import load_dotenv

from app.llm.openai.answer import generate_answer_openai

load_dotenv()

FAQ_QUESTIONS = [
    "Что вы сделали для ритейлеров?",
    "Что вы можете рассказать о себе?",
    "Какие у вас есть кейсы по компьютерному зрению?",
]

collection_name = "eora_openai"

faq_answers = {}
for q in FAQ_QUESTIONS:
    print(f"Генерирую ответ для: {q}")
    answer = generate_answer_openai(q, collection_name=collection_name)
    faq_answers[q] = answer

with open("faq_answers_openai.json", "w", encoding="utf-8") as f:
    json.dump(faq_answers, f, ensure_ascii=False, indent=2)
print("FAQ-ответы для OpenAI сохранены в faq_answers_openai.json")