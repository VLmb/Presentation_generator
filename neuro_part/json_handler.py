#название, количество слайдов
def neuro_gen_by_def_params(json_file):
    return json_file
#название, текст
def neuro_gen_by_text(json_file):
    return json_file
'''
Сгенерированный json можешь отправить в бэк можешь передать с помощью след кода:
headers = {"Content-Type": "application/json", "User-Agent": "MyApp"}
api_backend = "api_backend\create_presentation"
response = requests.post(api_backend, json=data, headers=headers)
data - json файл
'''