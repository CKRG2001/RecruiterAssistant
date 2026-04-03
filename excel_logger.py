import pandas as pd
import os


def log_rag(question, chunks, answer, file_path="rag_logs.xlsx"):
    # prepare row
    data = {
        "Question": question,
        "Chunk_1": chunks[0] if len(chunks) > 0 else "",
        "Chunk_2": chunks[1] if len(chunks) > 1 else "",
        "Chunk_3": chunks[2] if len(chunks) > 2 else "",
        "Answer": answer,
    }

    df_new = pd.DataFrame([data])

    # if file exists → append
    if os.path.exists(file_path):
        df_existing = pd.read_excel(file_path)
        df = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df = df_new

    df.to_excel(file_path, index=False)
