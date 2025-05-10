import vectorizer as v
from RAG import give_chunk_from_query as g
import slide_generator as sg


def neuro_gen_by_params(json_file: dict[str, any]) -> dict[str, any]:
    """
    Парсит json, после чего генерирует по нему презентацию
    :return: json информацией для презентации
    """
    presentation_title = json_file.get("Presentation_title", "")
    slides = json_file.get("Slides", [])
    slides_num = json_file.get("Slide_count", "")

    return sg.generate_presentation_by_params(slides_num, presentation_title, slides)


# название, текст
def neuro_gen_by_file(json_file: dict[str, any]) -> dict[str, any]:
    """
    Функция парсит json, потом векторизует информацию с файла пользователя
    После чего ищет по запросу пользователя наиболее подходящие чанки и по ним делает
    запрос в нейроонку
    :return: json информацией для презентации
    """
    presentation_title = json_file.get("Presentation_title", "")  # название презентации
    description = json_file.get("Description", "")  # текст файла, на основе которого делать презентацию
    slide_count = json_file.get("Slide_count", 1)  # количество слайдов

    v.save_chunks_with_vectors(text=description)
    chunks = g.find_similar_chunks(presentation_title)  # получаем чанки, соответствующие запросу названия презентации
    chunks = ''.join(chunks)

    json_file = sg.generate_presentation_by_file(chunks, slide_count, presentation_title)

    v.clear_db()

    return json_file


'''
Сгенерированный json можешь отправить в бэк можешь передать с помощью след кода:
headers = {"Content-Type": "application/json", "User-Agent": "MyApp"}
api_backend = "api_backend\create_presentation"
response = requests.post(api_backend, json=data, headers=headers)
data - json файл
'''
