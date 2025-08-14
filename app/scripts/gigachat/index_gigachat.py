from dotenv import load_dotenv

from app.llm.gigachat.chunk import get_all_chunks
from app.llm.gigachat.index import index_chunks_in_chroma_gigachat

load_dotenv()


chunks = get_all_chunks()
index_chunks_in_chroma_gigachat(chunks)
print("Индексация для GigaChat завершена!")