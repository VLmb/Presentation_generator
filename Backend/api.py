from flask import Blueprint, request, jsonify
from database import Presentation, Slide, db
from datetime import datetime
import requests

api_bp = Blueprint('api', __name__)

@api_bp.route('/create_presentation', methods=['POST'])
def create_presentation():
    data = request.get_json()

    name_of_presentation = data.get('Name of presentation')
    user_name = data.get('Name of creator')
    created_at = data.get('created_at')
    updated_at = data.get('updated_at')

    created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00")) if created_at else None
    updated_at = datetime.fromisoformat(updated_at.replace("Z", "+00:00")) if updated_at else None

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
        '!!!': "Эшкере",
        'id': presentation.id,
        'name_of_presentation': presentation.name_of_presentation,
        'user_name': presentation.user_name,
        'slides_count': len(slides_data)
    })

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