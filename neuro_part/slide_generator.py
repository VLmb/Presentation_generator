from gradio_client import Client
import json
import time
from loguru import logger
import sys
import vectorizer as v
from RAG import give_chunk_from_query as g
import json
import ast

def safe_parse_json(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        from loguru import logger
        logger.warning(f"json.loads не справился: {e}. Пробуем через ast.literal_eval")
        try:
            return ast.literal_eval(text)
        except Exception as ex:
            logger.error(f"Не удалось распарсить json даже через ast: {ex}")
            return {"Slides": ["Ошибка генерации презентации"]}

# Настройка логгера
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("presentation_generator.log", rotation="1 MB", compression="zip")

client = Client("Qwen/Qwen2.5")

SYSTEM_PROMPT = '''Вы — эксперт по созданию текста для презентаций. 
Ваша задача — генерировать контент для презентации на основе запроса пользователя.
Для каждого слайда предоставьте заголовок и описание в следующем формате:
"Slides": [{"Slide_title":  , "Slide_content":}]".
вот тебе пример json-ответа
  "Slides": [
    {
      "Slide_title": "текст заголовка",
      "Slide_content": "текст основной части"    
    }
]
по итогу, ты должен мне вернуть массив слайдов, для каждого есть два поля - Slide_title и Slide_content

Верните только указанное количество слайдов, каждый с уникальным заголовком и текстом, соответствующим теме. ответ 
возвращай в json формате. Если после "Предложения, на основе которых создавать слайды" есть текст, то генерируешь 
презентацию, преимущественно, на основе этого текста, если текст отсутствует, 
то генерируешь, ориентируясь лишь на название'''

RADIO = "72B"
API_NAME = "/model_chat"


def create_user_prompt(slides_num: str, pres_name: str, text='') -> str:
    prompt = (f"Создай презентацию с количеством слайдов: {slides_num}. "
              f"Тема презентации: {pres_name}. "
              f"Для каждого слайда придумай заголовок и описание."
              f"Предложения, на основе которых создавать слайды: {text}")
    logger.debug(f"Создан промпт пользователя: {prompt}")
    return prompt


def query_to_qwen(slides_num: any, pres_name: str, text='') -> dict[str, any]:
    """
    Делает запрос в нейросеть, формируя промпт пользователя, после возвращает
    текстовый ответ от нейросети
    """
    user_prompt = create_user_prompt(slides_num, pres_name, text)
    logger.info(f"Отправка запроса в Qwen для темы '{pres_name}' с {slides_num} слайдами...")
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

        logger.debug(f"Сырой ответ от нейросети: {text_answer}")

        # удаление мусора
        text_answer = text_answer.replace("`", "")
        text_answer = text_answer.replace("json\n", "")

        text_answer = safe_parse_json(text_answer)  # представляем ответ в виде словаря
        logger.success("Ответ успешно обработан и преобразован в JSON.")
        return text_answer

    except Exception as e:
        logger.exception(f"Ошибка при генерации презентации: {e}")
        return {"Slides": ["Ошибка генерации презентации"]}


def generate_presentation_by_params(slides_num, pres_name, slides) -> dict[str, any]:
    """
    Генерирует слайды по названиям, отправляя отдельный запрос на каждый слайд
    """
    result_slides = []
    logger.info(f"Начата поштучная генерация слайдов для темы '{pres_name}' ({slides_num} слайдов).")
    for slide in slides:
        slide_title = slide.get("Slide_title", "")
        logger.info(f"Генерация слайда: '{slide_title}'")
        response = query_to_qwen(slides_num, pres_name, slide_title)
        if response and "Slides" in response and len(response["Slides"]) > 0:
            slide_content = response["Slides"][0].get("Slide_content", "")
            logger.success(f"Слайд '{slide_title}' успешно сгенерирован.")
            result_slides.append({
                "Slide_title": slide_title,
                "Slide_content": slide_content
            })
        else:
            logger.warning(f"Не удалось сгенерировать слайд '{slide_title}'.")
            result_slides.append({
                "Slide_title": slide_title,
                "Slide_content": "Не удалось сгенерировать содержимое слайда."
            })
        time.sleep(1)  # Пауза между запросами, чтобы избежать перегрузки
    return {"Slides": result_slides}


def generate_presentation_from_file_with_titles_and_chunks(description, slides_num, pres_name) -> dict[str, any]:
    """
    Полная генерация презентации:
    - генерирует заголовки слайдов на основе текста
    - для каждого заголовка находит релевантные чанки
    - генерирует слайд по заголовку + чанкам
    """
    logger.info(f"Старт генерации по файлу: тема — '{pres_name}', количество слайдов — {slides_num}")

    v.save_chunks_with_vectors(description)

    logger.info("Запрос к нейросети для генерации заголовков слайдов...")
    slide_titles_json = query_to_qwen(slides_num, pres_name, description)
    slide_titles = [s["Slide_title"] for s in slide_titles_json.get("Slides", [])]

    result_slides = []

    for i, title in enumerate(slide_titles, 1):
        logger.info(f"[{i}/{len(slide_titles)}] Поиск чанков под заголовок '{title}'...")
        relevant_chunks = g.find_similar_chunks(title)
        text_for_slide = ' '.join(relevant_chunks)

        logger.info(f"Генерация слайда: '{title}'...")
        slide_response = query_to_qwen(1, title, text_for_slide)

        if "Slides" in slide_response and slide_response["Slides"]:
            slide = slide_response["Slides"][0]
            result_slides.append({
                "Slide_title": title,
                "Slide_content": slide.get("Slide_content", "Ошибка генерации текста.")
            })
            logger.success(f"Слайд '{title}' сгенерирован успешно.")
        else:
            result_slides.append({
                "Slide_title": title,
                "Slide_content": "Ошибка генерации текста."
            })
            logger.warning(f"Не удалось сгенерировать слайд '{title}'")

    v.clear_db()
    logger.success("Генерация завершена.")
    return {"Slides": result_slides}


if __name__ == "__main__":
    test_text = '''Вот тебе 10 чётких и развёрнутых тезисов про глобализацию — без воды, по существу и с разных 
    сторон:1. **Ускоренный обмен технологиями и знаниями**  Глобализация упростила доступ к современным технологиям, 
    исследованиям и образовательным ресурсам по всему миру. Это позволяет развивающимся странам быстрее сокращать 
    технологическое отставание.2. **Углубление международного разделения труда**  Страны специализируются на том, 
    что у них получается лучше всего (по Рикардо), а цепочки поставок растягиваются на весь мир. Например, 
    айфон проектируют в США, компоненты производят в Азии, собирают в Китае. 3. **Рост влияния транснациональных 
    корпораций (ТНК)** Гиганты вроде Google, Amazon, Nestlé и других действуют глобально и часто оказываются мощнее 
    государств. Они диктуют правила, меняют рынки и формируют тренды, выходящие за рамки национальных интересов. 4. 
    **Стирание культурных границ** Глобализация унифицирует потребление, музыку, кино, еду и одежду — от ТикТока до 
    фастфуда. Это создаёт "глобальную культуру", но может вести к эрозии локальных традиций и идентичности.. **Рост 
    экономического неравенства** Хотя в целом глобализация увеличивает мировой ВВП, она усиливает расслоение: крупные 
    города и образованные элиты выигрывают, а бедные и менее образованные регионы часто теряют позиции и рабочие 
    места. 6. **Уязвимость к глобальным кризисам** Связанность рынков делает всю систему хрупкой. Финансовые, 
    пандемические или логистические сбои в одной стране быстро отражаются на всей планете — как это было с COVID-19 и 
    кризисом микрочипов. 7. **Миграция рабочей силы и «утечка мозгов»** Специалисты уезжают в страны с лучшими 
    условиями, создавая дефицит кадров у себя на родине. Пример — ИТ-кадры из Восточной Европы и Индии массово 
    переезжают на Запад. 8. **Глобализация усиливает экологическую нагрузку** Интенсивное производство, логистика и 
    потребление вредят экологии. Развитые страны часто экспортируют грязные производства в менее защищённые по 
    экозаконам регионы. 9. **Рост политической и экономической зависимости** Некоторые страны теряют 
    самостоятельность, становясь экономически зависимыми от внешних рынков, инвестиций или технологий. Это 
    стратегическая уязвимость, особенно в условиях санкций или торговых войн. 10. **Контрдвижение — деглобализация** 
    Сегодня всё чаще появляются антиглобалистские тренды: протекционизм, санкции, возврат производств, локализация 
    IT. Это реакция на уязвимости глобального мира и попытка вернуть контроль над экономикой и суверенитетом.'''
    print(query_to_qwen("3", "проблемы кочевников", test_text))
    print("\n", generate_presentation_from_file_with_titles_and_chunks(test_text, 2, "влияние глобализации на кфс"))
    print("\n", generate_presentation_by_params(3, "влияние глобализации на растения",
                                                [{"Slide_title": "фикус"}, {"Slide_title": "гепсофилы"}]))
