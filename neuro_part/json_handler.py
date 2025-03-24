#название, количество слайдов
def parse_json_with_def_params(json_file):
    pass
#название, текст
def parse_json_with_text(json_file):
    pass

'''
Сгенерированный json можешь отправить в бэк можешь передать с помощью след кода:
headers = {"Content-Type": "application/json", "User-Agent": "MyApp"}
api_backend = "api_backend\create_presentation"
response = requests.post(api_backend, json=data, headers=headers)
data - json файл
'''