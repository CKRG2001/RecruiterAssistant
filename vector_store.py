import chromadb
from functools import lru_cache
from sentence_transformers import SentenceTransformer, CrossEncoder
from langchain_text_splitters import RecursiveCharacterTextSplitter
import re
from file_reader import load_resume


@lru_cache()
def get_embedding_model():
    # print("🔄 Loading embedding model...")
    return SentenceTransformer("all-MiniLM-L6-v2")


@lru_cache()
def get_cross_encoder():
    # print("🔄 Loading cross encoder...")
    return CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


class VectorStore:
    def __init__(self, collection_name="resume", db_path="VectorStore/"):
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection_name = collection_name

        self.embedding_model = get_embedding_model()
        self.cross_encoder = get_cross_encoder()

        self.collection = self.client.get_or_create_collection(self.collection_name)

    def chunk_text(self, text):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=200,
            chunk_overlap=50,
            separators=["\n\n", "\n", ". "],
        )
        return [c for c in splitter.split_text(text) if c]

    def get_embeddings(self, texts):
        return self.embedding_model.encode(texts)

    def create(self, text):
        try:
            self.client.delete_collection(self.collection_name)
        except:
            pass

        self.collection = self.client.create_collection(self.collection_name)

        chunks = self.chunk_text(text)
        embeddings = self.get_embeddings(chunks)

        self.collection.add(
            documents=chunks,
            embeddings=embeddings.tolist(),
            ids=[f"chunk_{i}" for i in range(len(chunks))],
        )

        return chunks

    def keyword_search(self, query, top_k=5):

        results = self.collection.get(include=["documents"])
        docs = results["documents"]

        scored = []
        query_terms = set(re.findall(r"\w+", query.lower()))

        for doc in docs:
            doc_terms = set(re.findall(r"\w+", doc.lower()))
            score = len(query_terms & doc_terms) / len(query_terms)
            if score > 0:
                scored.append((doc, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in scored[:top_k]]

    def rerank(self, query, chunks, top_k=5):
        pairs = [(query, chunk) for chunk in chunks]
        scores = self.cross_encoder.predict(pairs)

        ranked = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in ranked[:top_k]]

    def search(self, queries, top_k=5):

        all_results = []

        for query in queries:
            query_embedding = self.get_embeddings([query])[0]

            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=10,
                include=["documents"],
            )

            docs = results["documents"][0]
            all_results.extend(docs)

        keyword_results = self.keyword_search(queries[0], top_k)

        final_results = list(dict.fromkeys(all_results + keyword_results))

        return self.rerank(queries[0], final_results, top_k)


if __name__ == "__main__":
    resume_text = load_resume()
    vs = VectorStore()
    chunks = vs.create(resume_text)
    print(f"Created vector store with {len(chunks)} chunks.")
