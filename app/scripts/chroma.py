import os
import shutil

from chromadb.config import Settings

from chromadb import PersistentClient


def reset_chroma_db(path="chromadb"):
    """
    Полностью удаляет папку chromadb (все коллекции будут пересозданы с нуля).
    """
    if os.path.exists(path):
        shutil.rmtree(path)
        print(f"ChromaDB по пути '{path}' удалён.")

def get_chroma_client():
    return PersistentClient(path="chromadb", settings=Settings(allow_reset=True))

def get_or_create_collection(client, name):
    if name in [c.name for c in client.list_collections()]:
        return client.get_collection(name)
    return client.create_collection(name)