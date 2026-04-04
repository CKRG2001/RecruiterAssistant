import chromadb
from embedding import get_embeddings, chunk_text


# Initialize ChromaDB client and collection
client = chromadb.PersistentClient(path="VectorStore/")


def create_vectorstore(text, collection_name="resume"):
    try:
        client.delete_collection(collection_name)
    except:
        pass

    collection = client.create_collection(collection_name)

    chunks = chunk_text(text)
    embeddings = get_embeddings(chunks)

    collection.add(
        documents=chunks,
        embeddings=embeddings.tolist(),
        ids=[f"chunk_{i}" for i in range(len(chunks))],
    )
    print(f"Vector store created with {len(chunks)} chunks.")
    return collection


def collection_exists(collection_name="resume"):
    try:
        client.get_collection(collection_name)
        return True
    except:
        return False


def get_vectorstore(collection_name="resume"):
    try:
        collection = client.get_collection(collection_name)
        return collection
    except chromadb.errors.CollectionNotFoundError:
        print(f"Collection '{collection_name}' not found.")
        return None


def search_vectorstore(query, collection_name="resume", top_k=3):
    collection = get_vectorstore(collection_name)
    if collection is None:
        return []

    expanded_query = f"""{query} skills experience technologies tools"""
    query_embedding = get_embeddings([expanded_query])[0]

    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=top_k,
        include=["documents", "distances"],
    )
    documents = results["documents"][0]
    distances = results["distances"][0]

    filtered_docs = [doc for doc, dist in zip(documents, distances) if dist < 0.5]

    if not filtered_docs:
        filtered_docs = documents

    return filtered_docs
