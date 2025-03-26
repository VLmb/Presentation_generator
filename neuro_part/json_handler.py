from RAG.
#название, количество слайдов
def neuro_gen_by_def_params(json_file): #сделает Богдан с мишей
    return json_file
#название, текст
def neuro_gen_by_text(json_file):
    presentation_name = json_file.get("name")
    '''
    надо сделать, чтобы в функцию еще передавался файл(txt, docx, pdf)
    по нему мы будем делать поиск
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