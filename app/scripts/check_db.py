from app.scripts.chroma import get_chroma_client

if __name__ == "__main__":
    client = get_chroma_client()
    collections = client.list_collections()
    print("Коллекции в ChromaDB:", [c.name for c in collections])