import pandas as pd
import os


def log_rag(question, context, answer, file_path="rag_logs.xlsx"):
    # prepare row
    data = {
        "Question": question,
        "Context": context,
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
