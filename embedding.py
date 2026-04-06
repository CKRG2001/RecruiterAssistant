from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def chunk_text(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=250, chunk_overlap=50)

    lines = text.split("\n")
    chunks = []
    buffer = ""

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # If line is short → add to buffer
        if len(line) < 80:
            if len(buffer) + len(line) < 250:
                buffer += " " + line
            else:
                chunks.append(buffer.strip())
                buffer = line

        else:
            # flush buffer first
            if buffer:
                chunks.append(buffer.strip())
                buffer = ""

            if len(line) > 250:
                chunks.extend(splitter.split_text(line))
            else:
                chunks.append(line)

    # flush remaining buffer
    if buffer:
        chunks.append(buffer.strip())

    return chunks


# Embedding chunks using SentenceTransformer
def get_embeddings(chunks):
    embeddings = embedding_model.encode(chunks)
    return embeddings
