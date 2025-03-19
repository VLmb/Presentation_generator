from gradio_client import Client

client = Client("Qwen/Qwen2.5") # Нужен URL

SYSTEM_PROMPT = f'''Вы — эксперт по созданию текста для презентаций. 
Ваша задача — генерировать контент для презентации на основе запроса пользователя.
Для каждого слайда предоставьте заголовок и описание в следующем формате:
"Слайд [номер слайда][заголовок][описание].
Верните только указанное количество слайдов, каждый с уникальным заголовком и текстом, соответствующим теме.'''

RADIO = "72B"
API_NAME = "/model_chat"

def create_user_prompt(user_dict):
    prompt = (f"Создай презентацию с количеством слайдов: {user_dict['number_slide']}. "
              f"Тема презентации: {user_dict['title']}. "
              f"Для каждого слайда придумай заголовок и описание.")
    return prompt

def get_skills_based_on_input(user_dict):
    user_prompt = create_user_prompt(user_dict)
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
        return parse_text(text_answer)
    except Exception as e:
        print("ошибка",e)
        return None


def parse_text(text_answer):
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

