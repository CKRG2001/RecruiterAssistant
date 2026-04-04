import streamlit as st
from rag import load_resume
from excel_logger import log_rag
from llm import generate_summary, ask_question, correct_question
from vectorstore import (
    create_vectorstore,
    collection_exists,
    search_vectorstore,
    # get_vectorstore
)


st.set_page_config(page_title="Recruiter Assistant", page_icon="", layout="wide")


if st.button("← Back to Home"):
    st.switch_page("app.py")

if "chai_resume_text" not in st.session_state:
    st.session_state.chai_resume_text = load_resume()

if "rag_ready" not in st.session_state:
    if not collection_exists():
        with st.spinner("Loading Resume into Vector Store..."):
            create_vectorstore(st.session_state.chai_resume_text)
        st.success("Resume loaded into vector store successfully!")
    else:
        st.info("Using existing vector store")
    st.session_state.rag_ready = True


st.title("🧑‍💼 About me")
st.subheader("Summary")
if "chai_summary" not in st.session_state:
    with st.spinner("Generating Summary...would take a minute..."):
        st.session_state.chai_summary = generate_summary(
            st.session_state.chai_resume_text
        )
st.write(st.session_state.chai_summary)
st.markdown("---")

if "chai_messages" not in st.session_state:
    st.session_state.chai_messages = []

for msg in st.session_state.chai_messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

chai_question = st.chat_input(
    "Ask me anything about my experience, skills or education..."
)

if chai_question:
    with st.chat_message("user"):
        st.write(chai_question)

    modified_question = correct_question(chai_question)
    # Retrieve relevant chunks from vector store based on the question
    relevant_chunks = search_vectorstore(modified_question)

    # st.write(relevant_chunks)

    # if LLM fails to find relevant chunks, use full resume as context (fallback)
    if not relevant_chunks:
        context = st.session_state.chai_resume_text
        st.info(
            "Failed to find relevant information. Using full resume to generate answer."
        )
    else:
        context = "\n".join(relevant_chunks)

    # Generate answer using LLM with retrieved context
    with st.chat_message("assistant"):
        answer = st.write_stream(
            ask_question(context, chai_question, st.session_state.chai_messages)
        )

    log_rag(chai_question, relevant_chunks, answer)
    # save into chat history
    st.session_state.chai_messages.append({"role": "user", "content": chai_question})
    st.session_state.chai_messages.append({"role": "assistant", "content": answer})
