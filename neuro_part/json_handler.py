from RAG import vectorizer as v
from RAG import give_chunk_from_query as g

#название, количество слайдов
def neuro_gen_by_def_params(json_file): #сделает Богдан с мишей

    presentation_name = json_file.get('name')
    number_of_slides = json_file.get('slides') #


    return json_file
#название, текст
def neuro_gen_by_text(json_file):
    presentation_name = json_file.get("name") # название презентации
    file_text = json_file.get("text")  # текст файла, на основе которого делать презентацию
    number_of_slides = json_file.get("slides") # количество слайдов

    v.save_chunks_with_vectors(text=file_text)
    g.find_similar_chunks(presentation_name) # получаем чанки, соответствующие запросу названия презентации

    '''
    нам нужно обратиться к нейронке, вставляя в промпт наши чанки
    '''

    '''
    возвращаем json ответ нейронки
    '''

    return json_file


'''
Сгенерированный json можешь отправить в бэк можешь передать с помощью след кода:
headers = {"Content-Type": "application/json", "User-Agent": "MyApp"}
api_backend = "api_backend\create_presentation"
response = requests.post(api_backend, json=data, headers=headers)
data - json файл
'''