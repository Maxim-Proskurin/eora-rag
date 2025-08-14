from dotenv import load_dotenv

from app.llm.openai.chunk import get_all_chunks
from app.llm.openai.index import index_chunks_in_chroma_openai

load_dotenv()

chunks = get_all_chunks()
index_chunks_in_chroma_openai(chunks)
print("Индексация для OpenAI завершена!")