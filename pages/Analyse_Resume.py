import streamlit as st
from file_reader import extract_text
from llm import ask_question, generate_summary

st.set_page_config(page_title="Recruiter Assistant", page_icon="", layout="wide")

if st.button("← Back to Home"):
    st.switch_page("app.py")


st.title("🧑‍💼 Analyze any Candidate Resume")
st.markdown("Upload a resume to ask questions or generate a summary.")
st.markdown("---")

# Side Bar
with st.sidebar:
    st.markdown("### Options")
    if st.button("🔄 Clear & Upload New Resume", use_container_width=True):
        st.session_state.messages = []
        if "summary" in st.session_state:
            del st.session_state["summary"]
        st.rerun()


# File Upload and chat window
uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])

if uploaded_file:
    resume_text = extract_text(uploaded_file)

    if resume_text is None:
        st.error("Unsupported File Type")
        st.stop()

    st.success("Resume Uploaded Succesfully!")

    # Auto Generate Summary
    with st.spinner("Generating Summary..."):
        if "summary" not in st.session_state:
            st.session_state.summary = generate_summary(resume_text)
    with st.expander("Candidate Summary", expanded=True):
        st.write(st.session_state.summary)
    st.markdown("---")

    # Chat interface
    st.subheader("Ask anything about this candidate")

    # initializing chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # dispay chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    question = st.chat_input("Ask a question about the candidate...")

    if question:
        # display user question in chat
        with st.chat_message("user"):
            st.write(question)

        # get answer
        with st.chat_message("assistant"):
            answer = st.write_stream(
                ask_question(resume_text, question, st.session_state.messages)
            )

        # store assistant question/answer in chat history
        st.session_state.messages.append({"role": "user", "content": question})
        st.session_state.messages.append({"role": "assistant", "content": answer})
