# utils/document_loader.py
import pdfplumber
from io import BytesIO

def extract_text_from_file(uploaded_file):
    text = ""
    if uploaded_file.name.endswith(".pdf"):
        with pdfplumber.open(BytesIO(uploaded_file.read())) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    elif uploaded_file.name.endswith(".txt"):
        text = uploaded_file.read().decode("utf-8")
    return text.strip()