import ollama


def ask_question(resume_text, question, chat_history=None):
    if chat_history is None:
        chat_history = []
    try:
        messages = [
            {
                "role": "system",
                "content": f"""
                    You are a recruitment assistant. 
                    Answer the questions asked based on the resume provided and chat history when relavent. 
                    Rules:
                        - Keep answers short and to the point
                        - No bullet points unless specifically asked
                        - No extra explanation or elaboration
                        - If the answer is not in the resume, say "Not mentioned in the resume"
                        - Never make assumptions beyond what is written
                    Resume:{resume_text}
                """,
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
        prompt = f"""
        You are a recruitment assistant. Based on the resume below, provide a structured summary.
        
        Rules:
        - Refer to the candidate by their name only, never use he/she/his/her
        - Be concise and factual
        - Do not add any intro or outro lines
        - Strictly follow the format below
        
        Format:
        **Summary:** Generate a 3-4 sentence professional summary
        
        **Top 5 Skills:** skill1, skill2, skill3, skill4, skill5
        
        **Years of Experience:** X years Y months
        
        **Most Recent Role:** Job Title at Company (dates)
        
        Resume:
        {resume_text}
        """

        response = ollama.chat(
            model="llama3.2", messages=[{"role": "user", "content": prompt}]
        )

        return response["message"]["content"]

    except ollama.ResponseError as e:
        return f"Model error: {e}"

    except ConnectionError:
        return "Connection error: Unable to reach the model server. Make sure the 'Ollama serve' is running and accessible."

    except Exception as e:
        return f"An unexpected error occurred: {e}"
