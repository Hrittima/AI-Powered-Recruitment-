import os

def extract_text(filepath: str) -> str:
    """
    Extract raw text from PDF or DOCX.
    Tries pdfplumber first (better accuracy), falls back to PyPDF2.
    """
    ext = os.path.splitext(filepath)[1].lower()

    if ext in (".doc", ".docx"):
        return _extract_docx(filepath)
    else:
        return _extract_pdf(filepath)


def _extract_pdf(filepath: str) -> str:
    # ── Primary: pdfplumber ─────────────────────────────────────────────
    try:
        import pdfplumber
        text = ""
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if text.strip():
            return text.lower()
    except Exception as e:
        print(f"pdfplumber failed: {e}")

    # ── Fallback: PyPDF2 ────────────────────────────────────────────────
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(filepath)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.lower()
    except Exception as e:
        print(f"PyPDF2 failed: {e}")

    return ""


def _extract_docx(filepath: str) -> str:
    try:
        from docx import Document
        doc = Document(filepath)
        return "\n".join(p.text for p in doc.paragraphs).lower()
    except Exception as e:
        print(f"docx extraction failed: {e}")
        return ""