from app.scripts.chroma import get_chroma_client, get_or_create_collection


def main():
    client = get_chroma_client()
    collection = get_or_create_collection(client, "eora_gigachat")
    print("Документов в коллекции:", collection.count())
    results = collection.get(include=["documents", "metadatas"], limit=10)
    documents = results.get("documents") or []
    metadatas = results.get("metadatas") or []
    for i, (doc, meta) in enumerate(zip(documents, metadatas), 1):
        title = meta.get('title', '')
        print(f"[{i}] {meta.get('source', '')} | {title}: {doc[:120]}...")

if __name__ == "__main__":
    main()