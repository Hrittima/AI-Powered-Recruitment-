from PyPDF2 import PdfReader

def extract_text(filepath):
    try:
        reader = PdfReader(filepath)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.lower()
    except:
        return ""