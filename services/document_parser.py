from pathlib import Path

from pypdf import PdfReader
from docx import Document


def extract_text(filepath, file_type):
    """
    Извлекает текст из PDF, DOCX или TXT.
    """

    file_type = file_type.lower()

    if file_type == "pdf":
        return extract_pdf(filepath)

    if file_type == "docx":
        return extract_docx(filepath)

    if file_type == "txt":
        return extract_txt(filepath)

    return ""


def extract_pdf(filepath):
    """
    Извлечение текста из PDF.
    """

    reader = PdfReader(filepath)

    pages = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            pages.append(text)

    return "\n\n".join(pages)


def extract_docx(filepath):
    """
    Извлечение текста из DOCX.
    """

    document = Document(filepath)

    paragraphs = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            paragraphs.append(paragraph.text)

    return "\n\n".join(paragraphs)


def extract_txt(filepath):
    """
    Извлечение текста из TXT.
    """

    path = Path(filepath)

    return path.read_text(
        encoding="utf-8",
        errors="ignore"
    )