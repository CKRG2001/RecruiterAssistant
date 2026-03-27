import PyPDF2
import docx


def extract_text(uploaded_file):
    file_name = uploaded_file.name.lower()

    # When file is PDF Format
    if file_name.endswith(".pdf"):
        reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            extracted_page = page.extract_text()
            if extracted_page:  # Exclude empty pages(information)
                text += extracted_page
        return text.strip()

    # When file is in Word Format
    elif file_name.endswith(".docx"):
        doc = docx.Document(uploaded_file)
        text = ""
        for para in doc.paragraphs:
            extracted_para = para.text
            if extracted_para:  # Exclude empty information
                text += extracted_para + "\n"
        return text.strip()

    return None
