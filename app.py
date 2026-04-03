import streamlit as st

# Page Configuration
st.set_page_config(page_title="Recruiter Assistant", page_icon="💼", layout="wide")

# Header Section
st.markdown(
    """
    <h1 style='text-align: center;'>Recruiter Assistant</h1>
    <p style='text-align: center; font-size:18px;'>
        AI-powered platform for intelligent resume analysis and candidate insights
    </p>
    <hr>
""",
    unsafe_allow_html=True,
)

# Main Layout
col1, col2 = st.columns(2, gap="large")

# --- Column 1 ---
with col1:
    st.markdown("## 📄 Ask about Chaitanya")

    st.markdown("""
    **Explore pre-analyzed candidate profile**
    
    - Access a pre-uploaded resume  
    - View auto-generated summary
    - Ask detailed questions about skills, experience, and background  
    - Powered by a RAG pipeline and Ollama LLM
    """)

    st.markdown("")

    if st.button("🔍 Explore Chaitanya's Profile", use_container_width=True):
        st.switch_page("pages/Ask_Chaitanya.py")

# --- Column 2 ---
with col2:
    st.markdown("## 📑 Analyze New Candidate")

    st.markdown("""
    **Upload and evaluate any candidate resume**
    
    - Supports PDF and DOCX formats  
    - Automatically generates candidate summaries  
    - Interactive Q&A about candidate details  
    - Powered by Ollama LLM  
    """)

    st.markdown("")

    if st.button("📊 Analyze Other Candidate Resume", use_container_width=True):
        st.switch_page("pages/Analyse_Resume.py")

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown(
    """
    <p style='text-align: center; color: gray; font-size: 0.9rem;'>
        Built by <b>Chaitanya Kumar Reddy Goukanapalli</b> 
        &nbsp;|&nbsp; 
        <a href='https://github.com/CKRG2001' style='color: gray;'>GitHub</a>
        &nbsp;|&nbsp;
        <a href='https://www.linkedin.com/in/chaitanya-reddy-genai/' style='color: gray;'>LinkedIn</a>
    </p>
""",
    unsafe_allow_html=True,
)
