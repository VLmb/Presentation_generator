import os
import fitz
import docx

def read_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    return text


def read_docx(file_path):
    doc = docx.Document(file_path)
    text = " ".join([para.text for para in doc.paragraphs if para.text.strip()])
    return text


def read_pdf(file_path):
    doc = fitz.open(file_path)
    text = " ".join([page.get_text("text") for page in doc])
    return text


def take_text(file_path):
    ext = os.path.splitext(file_path)[-1].lower()

    '''
    Надо сделать так, чтобы функция брала файл, после прочтения файла, записывала резултат в json
    Артем, это на тебе, ибо ты составляешь json
    '''

    match ext:
        case ".txt":
            chunks = read_txt(file_path)
        case ".docx":
            chunks = read_docx(file_path)
        case ".pdf":
            chunks = read_pdf(file_path)
        case _:
            raise ValueError("Неподдерживаемый формат файла")

    pass

#    return json

