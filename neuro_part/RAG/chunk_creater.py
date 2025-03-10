import os
import fitz
import docx
import re

def split_into_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)  # Разбиваем текст на предложения
    return [s.strip() for s in sentences if s.strip()]


def group_sentences(sentences, group_size=3):
    return [" ".join(sentences[i:i + group_size]) for i in range(0, len(sentences), group_size)]


def read_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    sentences = split_into_sentences(text)
    return group_sentences(sentences)


def read_docx(file_path):
    doc = docx.Document(file_path)
    text = " ".join([para.text for para in doc.paragraphs if para.text.strip()])
    sentences = split_into_sentences(text)
    return group_sentences(sentences)


def read_pdf(file_path):
    doc = fitz.open(file_path)
    text = " ".join([page.get_text("text") for page in doc])
    sentences = split_into_sentences(text)
    return group_sentences(sentences)


def split_text_by_sentences(file_path):
    ext = os.path.splitext(file_path)[-1].lower()

    match ext:
        case ".txt":
            chunks = read_txt(file_path)
        case ".docx":
            chunks = read_docx(file_path)
        case ".pdf":
            chunks = read_pdf(file_path)
        case _:
            raise ValueError("Неподдерживаемый формат файла")

    return chunks

