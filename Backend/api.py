import requests
from flask import Blueprint, request, jsonify
from database import Presentation, Slide, db
from datetime import datetime

api_bp = Blueprint('api_backend', __name__)
api_neuro_part = "api_neuro_part"
params = "/gen_by_def_params"
text = "/gen_by_text"

# @api_bp.route('/create_presentation_by_text', methods=['POST'])
# def create_presentation_by_text

@api_bp.route('/gen_presentation_by_title', methods=['POST'])
def gen_presentation_by_params():
    data = request.get_json()

    name_of_presentation = data.get("Presentation_title")
    name_of_creator = "User_1"

    headers = {"Content-Type": "application/json", "User-Agent": "MyApp"}
    response = requests.post("http://127.0.0.1:5001/api_neuro_part/gen_by_def_params", json=data, headers=headers)

    print("Статус код:", response.status_code)
    print("Ответ сервера:", response.text)

    answer = response.json()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    updated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    presentation = Presentation(
        user_name=name_of_creator,
        name_of_presentation=name_of_presentation,
        created_at=created_at,
        updated_at=updated_at
    )
    db.session.add(presentation)
    db.session.flush()

    slides_data = answer.get('slides', [])
    for index, slide_data in enumerate(slides_data, start=1):
        slide = Slide(
            presentation_id=presentation.id,
            theme="Theme_1",     #slide_data.get('theme'),
            title=slide_data.get('Slide_title'),
            title_font="Normal",  #slide_data.get('title_font')
            title_font_size=16,  #slide_data.get('title_font_size'),
            content=slide_data.get('Slide_content'),
            content_font="Normal",  #slide_data.get('content_font'),
            content_font_size=14,  #slide_data.get('content_font_size'),
            images="null" #slide_data.get('images_url', [])
        )
        db.session.add(slide)

    db.session.commit()

    return answer

@api_bp.route('/gen_presentation_by_text', methods=['POST'])
def gen_presentation_by_text():
    data = request.get_json()

    name_of_presentation = data.get("Presentation_title")
    name_of_creator = "User_1"

    headers = {"Content-Type": "application/json", "User-Agent": "MyApp"}
    response = requests.post("http://127.0.0.1:5001/api_neuro_part/gen_by_text", json=data, headers=headers)

    answer = response.json()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    updated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    presentation = Presentation(
        user_name=name_of_creator,
        name_of_presentation=name_of_presentation,
        created_at=created_at,
        updated_at=updated_at
    )
    db.session.add(presentation)
    db.session.flush()

    slides_data = answer.get('slides', [])
    for index, slide_data in enumerate(slides_data, start=1):
        slide = Slide(
            presentation_id=presentation.id,
            theme="Theme_1",  # slide_data.get('theme'),
            title=slide_data.get('Slide_title'),
            title_font="Normal",  # slide_data.get('title_font')
            title_font_size=16,  # slide_data.get('title_font_size'),
            content=slide_data.get('Slide_content'),
            content_font="Normal",  # slide_data.get('content_font'),
            content_font_size=14,  # slide_data.get('content_font_size'),
            images="null"  # slide_data.get('images_url', [])
        )
        db.session.add(slide)

    db.session.commit()

    return answer

@api_bp.route('/create_presentation', methods=['POST'])
def create_presentation():
    data = request.get_json()

    name_of_presentation = data.get('Name of presentation')
    user_name = data.get('Name of creator')

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    updated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    presentation = Presentation(
        user_name=user_name,
        name_of_presentation=name_of_presentation,
        created_at = created_at,
        updated_at = updated_at
    )
    db.session.add(presentation)
    db.session.flush()

    slides_data = data.get('slides', [])
    for index, slide_data in enumerate(slides_data, start = 1):
        slide = Slide(
            presentation_id=presentation.id,
            theme=slide_data.get('theme'),
            title=slide_data.get('title'),
            title_font = slide_data.get('title_font'),
            title_font_size = slide_data.get('title_font_size'),
            content=slide_data.get('content'),
            content_font=slide_data.get('content_font'),
            content_font_size=slide_data.get('content_font_size'),
            images=slide_data.get('images_url', [])
        )
        db.session.add(slide)

    db.session.commit()

    return jsonify({
        '!!!': "Эшкере  ",
        'id': presentation.id,
        'name_of_presentation': presentation.name_of_presentation,
        'user_name': presentation.user_name,
        'slides_count': len(slides_data)
    })

# Получение презентации по ID
@api_bp.route('/get_presentation/<int:id>', methods=['GET'])
def get_presentation(id):
    presentation = Presentation.query.get_or_404(id)

    slides = Slide.query.filter_by(presentation_id=id).all()

    return jsonify({
        'id': presentation.id,
        'name_of_presentation': presentation.name_of_presentation,
        'user_name': presentation.user_name,
        'created_at': presentation.created_at.isoformat(),
        'updated_at': presentation.updated_at.isoformat(),
        'slides': [
            {
                'slide_number': index,
                'theme': slide.theme,
                'title': slide.title,
                'title_font': slide.title_font,
                'title_font_size': slide.title,
                'content': slide.content,
                'content_font': slide.content_font,
                'content_font_size': slide.content_font_size,
                'images': slide.images
            } for index, slide in enumerate(slides, start = 1)
        ]
    })

#Получение всех презентаций конкретного пользователя
@api_bp.route('/get_presentations_all/<string:user_name>', methods = ['GET'])
def get_presentations_all(user_name):
    presentations = Presentation.query.filter_by(user_name = user_name).all()

    if not presentations:
        return jsonify({
            'message': f"Презентаций для пользователя {user_name} не найдено",
            'presentations': []
        }), 404

    return jsonify({
        'user_name': user_name,  # Используем переменную user_name
        'presentations': [
            {
                'id': presentation.id,
                'name_of_presentation': presentation.name_of_presentation,
                'created_at': presentation.created_at.isoformat(),  # Преобразуем в строку
                'updated_at': presentation.updated_at.isoformat(),  # Добавляем updated_at
                'slides_count': Slide.query.filter_by(presentation_id=presentation.id).count()  # Количество слайдов
            } for presentation in presentations
        ]
    })