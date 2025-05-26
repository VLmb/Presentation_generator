import re


def split_into_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)  # Разбиваем текст на предложения
    return [s.strip() for s in sentences if s.strip()]


def group_sentences(sentences, group_size=3):
    return [" ".join(sentences[i:i + group_size]) for i in range(0, len(sentences), group_size)]


def text_to_chunks(text: str) -> list:
    sentences = split_into_sentences(text)
    chunks = group_sentences(sentences)

    return chunks