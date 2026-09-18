import os

import fitz
from docx import Document

from app.services.ocr_service import extract_text_from_image


def extract_text_from_pdf(filepath):
    text = ""

    pdf = fitz.open(filepath)

    for page in pdf:
        text += page.get_text()

    pdf.close()

    return text


def extract_text_from_docx(filepath):
    document = Document(filepath)

    text = []

    for paragraph in document.paragraphs:
        text.append(paragraph.text)

    return "\n".join(text)


def extract_text_from_txt(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        return file.read()


def extract_text(filepath):
    extension = os.path.splitext(filepath)[1].lower()

    if extension == ".pdf":
        return extract_text_from_pdf(filepath)

    elif extension == ".docx":
        return extract_text_from_docx(filepath)

    elif extension == ".txt":
        return extract_text_from_txt(filepath)

    elif extension in [".jpg", ".jpeg", ".png"]:
        return extract_text_from_image(filepath)

    else:
        raise ValueError("Unsupported file format")