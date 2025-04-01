from gradio_client import Client

client = Client("Qwen/Qwen2.5") # Нужен URL

SYSTEM_PROMPT = f'''Вы — эксперт по созданию текста для презентаций. 
Ваша задача — генерировать контент для презентации на основе запроса пользователя.
Для каждого слайда предоставьте заголовок и описание в следующем формате:
"Слайд [номер слайда][заголовок][описание]".
Верните только указанное количество слайдов, каждый с уникальным заголовком и текстом, соответствующим теме.
ответ возвращай в json формате. Если после "Предложения, на основе которых создавать слайды" есть текст, то генерируешь
презентацию ТОЛЬКО на основе этого текста, если текст отсутствует, то генерируешь, ориентируясь лишь на название
'''# добавить формата пример

RADIO = "72B"
API_NAME = "/model_chat"

def create_user_prompt(slides_num, pres_name, text='') -> str:
    prompt = (f"Создай презентацию с количеством слайдов: {slides_num}. "
              f"Тема презентации: {pres_name}. "
              f"Для каждого слайда придумай заголовок и описание."
              f"Предложения, на основе которых создавать слайды: {text}")
    return prompt


def query_to_qwen(slides_num, pres_name, text=''):
    '''
    Делает запрос в нейросеть, формируя промпт пользователя, после возвращает
    текстовый ответ от нейросети
    '''

    user_prompt = create_user_prompt(slides_num, pres_name, text='')
    try:
        result = client.predict(
            query=user_prompt,
            system=SYSTEM_PROMPT,
            radio=RADIO,
            api_name=API_NAME
        )
        if isinstance(result, tuple):
            text_answer = result[1][0][-1]['text']
        else:
            text_answer = result
        print("презентация",text_answer)
        #return parse_text(text_answer) - миши вариация
        return text_answer
    except Exception as e:
        print("ошибка",e)
        return None


def parse_text(text_answer):
    '''
    Парсит ответ нейросети
    (вероятнее всего, функцию надо будет переделать, чтобы она делала json)
    '''

    try:
        slides = text_answer.split("слайд")[1:]
        results = []
        for slide in slides:
            lines = slide.strip().split("\n")
            if len(lines)>=2:
                title = lines[0].strip()
                description = "\n".join(lines[1:]).strip().split("\n")
                results.append({"title":title,"text":description})
        return results

    except Exception:
        return [{"title":"ошибка","text":text_answer}]
