from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


# Chunking text into smaller pieces with
def chunk_text(text, chunk_size=500, chunk_overlap=50):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    chunks = splitter.split_text(text)
    return chunks


# Embedding chunks using SentenceTransformer
def get_embeddings(chunks):
    embeddings = embedding_model.encode(chunks)
    return embeddings
