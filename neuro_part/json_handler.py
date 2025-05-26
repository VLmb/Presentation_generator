import vectorizer as v
from RAG import give_chunk_from_query as g
import slide_generator as sg
from loguru import logger



def neuro_gen_by_params(json_file: dict[str, any]) -> dict[str, any]:
    """
    Парсит json, после чего генерирует по нему презентацию
    :return: json информацией для презентации
    """
    presentation_title = json_file.get("Presentation_title", "")
    slides = json_file.get("Slides", [])
    slides_num = json_file.get("Slide_count", "")

    return sg.generate_presentation_by_params(slides_num, presentation_title, slides)



def neuro_gen_by_file(json_file: dict[str, any]) -> dict[str, any]:
    """
    Обёртка: вызывает расширенную генерацию по файлу с поиском заголовков и чанков.
    """
    from slide_generator import generate_presentation_from_file_with_titles_and_chunks

    presentation_title = json_file.get("Presentation_title", "")
    description = json_file.get("Description", "")
    slide_count = json_file.get("Slide_count", 1)

    return generate_presentation_from_file_with_titles_and_chunks(description, slide_count, presentation_title)




'''
Сгенерированный json можешь отправить в бэк можешь передать с помощью след кода:
headers = {"Content-Type": "application/json", "User-Agent": "MyApp"}
api_backend = "api_backend\create_presentation"
response = requests.post(api_backend, json=data, headers=headers)
data - json файл
'''
