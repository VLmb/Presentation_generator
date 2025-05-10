import vectorizer as v
from RAG import give_chunk_from_query as g
import slide_generator as sg

def neuro_gen_by_def_params(json_file):

    presentation_title = json_file.get("Presentation_title")
    slides = json_file.get("Slides")

    return sg.generate_presentation_by_titles(presentation_title, slides)

'''
надо еще парсить slides и для каждого слайда slide title
'''

#название, текст
def neuro_gen_by_text(json_file):
    presentation_title = json_file.get("Presentation_title", "")  # название презентации
    description = json_file.get("Description", "")  # текст файла, на основе которого делать презентацию
    slide_count = json_file.get("Slide_count", 1)  # количество слайдов

    v.save_chunks_with_vectors(text=description)
    chunks = g.find_similar_chunks(presentation_title)  # получаем чанки, соответствующие запросу названия презентации
    chunks = ''.join(chunks)

    json_file = sg.generate_presentation_by_description(chunks, slide_count, presentation_title)

    v.clear_db()

    return json_file


'''
Сгенерированный json можешь отправить в бэк можешь передать с помощью след кода:
headers = {"Content-Type": "application/json", "User-Agent": "MyApp"}
api_backend = "api_backend\create_presentation"
response = requests.post(api_backend, json=data, headers=headers)
data - json файл
'''