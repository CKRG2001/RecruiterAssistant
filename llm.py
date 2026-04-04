import ollama
from prompts import (
    question_correction_prompt,
    answer_generation_prompt,
    summary_generation_prompt,
)


# This function is used to optimize user questions for better resume retrieval
def correct_question(user_question):
    try:
        response = ollama.chat(
            model="llama3.2",
            messages=[
                {
                    "role": "user",
                    "content": question_correction_prompt.format(
                        user_question=user_question
                    ),
                }
            ],
        )

        return response["message"]["content"].strip()

    except ollama.ResponseError as e:
        return f"Model error: {e}"

    except ConnectionError:
        return "Connection error: Unable to reach the model server. Make sure the 'Ollama serve' is running and accessible."

    except Exception as e:
        return f"An unexpected error occurred: {e}"


# This function o
def ask_question(context, question, chat_history=None):

    if chat_history is None:
        chat_history = []
    try:
        messages = [
            {
                "role": "system",
                "content": answer_generation_prompt.format(context=context),
            }
        ]
        # providing chat history for memory
        for message in chat_history:
            messages.append({"role": message["role"], "content": message["content"]})

        # adding user question to message
        messages.append({"role": "user", "content": question})

        # Get Streaming response from model
        stream = ollama.chat(model="llama3.2", messages=messages, stream=True)

        for chunk in stream:
            yield chunk["message"]["content"]

    except ollama.ResponseError as e:
        return f"Model error: {e}"

    except ConnectionError:
        return "Connection error: Unable to reach the model server. Make sure the 'Ollama serve' is running and accessible."

    except Exception as e:
        return f"An unexpected error occurred: {e}"


def generate_summary(resume_text):
    try:
        response = ollama.chat(
            model="llama3.2",
            messages=[
                {
                    "role": "user",
                    "content": summary_generation_prompt.format(
                        resume_text=resume_text
                    ),
                }
            ],
        )

        return response["message"]["content"]

    except ollama.ResponseError as e:
        return f"Model error: {e}"

    except ConnectionError:
        return "Connection error: Unable to reach the model server. Make sure the 'Ollama serve' is running and accessible."

    except Exception as e:
        return f"An unexpected error occurred: {e}"
