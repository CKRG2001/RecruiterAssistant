import streamlit as st
from file_reader import extract_text


st.set_page_config(page_title="Recruiter Assistant", page_icon="", layout="wide")
st.title("🧑‍💼 Recruiter Assistant")
st.markdown("Upload a resume to get started")

uploaded_file = st.file_uploader("Upload Resume", type=["pdf", ".docx"])

if uploaded_file:
    text = extract_text(uploaded_file)

    if text is None:
        st.error("Unsupported File Type")
    elif text == "":
        st.warning("Couldnt extract text from file!")
    else:
        st.success(f"""File Extracted Succesfully! \n {len(text)} Characters""")
        with st.expander("View Extracted Text"):
            st.write(text)
