import hashlib
import streamlit as st
import time
from file_reader import load_resume, extract_text
from excel_logger import log_rag
from llm import generate_summary, json_extraction, ask_question, expand_query
from vector_store import VectorStore


st.set_page_config(
    page_title="Recruiter Assistant",
    page_icon="💼",
    layout="wide",
)


def make_collection_name(text, prefix="resume"):
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{digest}"


def reset_chat():
    for key in [
        "active_resume_text",
        "active_summary",
        "active_json_resume",
        "active_messages",
        "active_collection_name",
        "active_rag_ready",
    ]:
        st.session_state.pop(key, None)


st.title("💼 Recruiter Assistant")
st.caption(
    "Ask resume-aware questions about Chaitanya by default, or upload another candidate resume."
)

with st.sidebar:
    st.header("Candidate Source")

    source = st.radio(
        "Choose resume",
        ["Chaitanya's Resume", "Upload Candidate Resume"],
        index=0,
    )

    if st.button("Clear Chat", use_container_width=True):
        st.session_state.active_messages = []
        st.rerun()


if source == "Chaitanya's Resume":
    resume_text = load_resume()
    candidate_label = "Chaitanya"
    collection_name = "chaitanya_resume"

else:
    uploaded_file = st.sidebar.file_uploader(
        "Upload candidate resume",
        type=["pdf", "docx"],
    )

    if not uploaded_file:
        st.info("Upload a candidate resume, or switch back to Chaitanya's Resume.")
        st.stop()

    resume_text = extract_text(uploaded_file)

    if not resume_text:
        st.error("Could not extract text from the uploaded resume.")
        st.stop()

    candidate_label = uploaded_file.name
    collection_name = make_collection_name(resume_text, prefix="uploaded_resume")


if (
    st.session_state.get("active_collection_name") != collection_name
    or st.session_state.get("active_resume_text") != resume_text
):
    st.session_state.active_resume_text = resume_text
    st.session_state.active_collection_name = collection_name
    st.session_state.active_summary = None
    st.session_state.active_json_resume = None
    st.session_state.active_messages = []
    st.session_state.active_rag_ready = False


vs = VectorStore(collection_name=collection_name)

if not st.session_state.active_rag_ready:
    with st.spinner("Preparing vector store..."):
        result = vs.create(resume_text)

    if isinstance(result, dict) and result.get("skipped"):
        st.info(result["message"])
    else:
        st.success("Resume loaded into vector store.")

    st.session_state.active_rag_ready = True


st.subheader(f"Candidate: {candidate_label}")

if not st.session_state.active_json_resume:
    with st.spinner("Extracting structured resume data..."):
        st.session_state.active_json_resume = json_extraction(resume_text)

if not st.session_state.active_summary:
    with st.spinner("Generating summary..."):
        st.session_state.active_summary = st.write_stream(generate_summary(resume_text))

with st.expander("Candidate Summary", expanded=False):
    st.write(st.session_state.active_summary)


if "active_messages" not in st.session_state:
    st.session_state.active_messages = []


for message in st.session_state.active_messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


question = st.chat_input("Ask a question about this candidate...")

if question:
    start = time.perf_counter()
    with st.chat_message("user"):
        st.write(question)

    expanded_query = [question] + expand_query(
        question,
        st.session_state.active_summary,
    )

    relevant_chunks = vs.search(expanded_query)

    with st.expander("🔍 Retrieved Context", expanded=False):
        st.write(relevant_chunks)

    if not relevant_chunks:
        context = resume_text
        st.info("Could not find relevant chunks. Using full resume as fallback.")
    else:
        context = "\n\n---\n\n".join(relevant_chunks)

    with st.chat_message("assistant"):
        answer = st.write_stream(
            ask_question(
                context=context,
                structured_json=st.session_state.active_json_resume,
                question=question,
                chat_history=st.session_state.active_messages,
            )
        )
    end = time.perf_counter()
    log_rag(
        question=question,
        context=context,
        answer=answer,
        time_taken=round(end - start, 2),
    )

    st.session_state.active_messages.append({"role": "user", "content": question})
    st.session_state.active_messages.append({"role": "assistant", "content": answer})
