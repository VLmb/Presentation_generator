from flask import Blueprint, request, jsonify
from sqlalchemy import func
from database import Presentation, Slide, db
from datetime import datetime
import requests
import logging

# Настройка логирования
logging.basicConfig(
    filename='api.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s'
)

api_bp = Blueprint('api_backend', __name__)

@api_bp.route('/gen_presentation_by_title', methods=['POST'])
def gen_presentation_by_params():
    logging.debug(f'Starting /gen_presentation_by_title for request: {request.data[:200]}...') # Логируем начало запроса
    try:
        data = request.get_json()
        if not data:
            logging.warning('No JSON data provided for /gen_presentation_by_title')
            return jsonify({'error': 'No JSON data provided'}), 400

        name_of_presentation = data.get("Presentation_title", "Untitled Presentation")
        name_of_creator = data.get("user_name", "User_1")

        logging.debug(f'Calling external API for presentation: {name_of_presentation}')
        answer = None
        try:
            headers = {"Content-Type": "application/json", "User-Agent": "MyApp/1.0"}
            response = requests.post(
                "http://127.0.0.1:5001/api_neuro_part/gen_by_def_params",
                json=data,
                headers=headers,
                timeout=30000
            )
            response.raise_for_status()
            answer = response.json()
            logging.debug(f'External API call successful for {name_of_presentation}')
        except requests.RequestException as e:
            logging.error(f'External API error in /gen_presentation_by_title: {str(e)}')
            return jsonify({'error': f'External API error: {str(e)}'}), 500

        try:
            presentation = Presentation(
                user_name=name_of_creator,
                name_of_presentation=name_of_presentation,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(presentation)
            db.session.flush()

            slides_data = answer.get('Slides', [])
            if not slides_data:
                logging.warning(f"No slides data received from external API for presentation: {name_of_presentation}")

            for slide_data in slides_data:
                slide = Slide(
                    presentation_id=presentation.id,
                    theme=slide_data.get('Slide_theme', "Theme_1"),
                    title=slide_data.get('Slide_title', 'Untitled Slide'),
                    title_font=slide_data.get('Slide_title_font', "Normal"),
                    title_font_size=slide_data.get('Slide_title_font_size', 16),
                    content=slide_data.get('Slide_content', ''),
                    content_font=slide_data.get('Slide_content_font', "Normal"),
                    content_font_size=slide_data.get('Slide_content_font_size', 14),
                    images=slide_data.get('Slide_images', [])
                )
                db.session.add(slide)

            db.session.commit()
            logging.debug(f'Database commit successful for /gen_presentation_by_title ({name_of_presentation})')
        except Exception as db_exc:
            db.session.rollback()
            logging.error(f'Database operation error in /gen_presentation_by_title after API call: {str(db_exc)}', exc_info=True)
            return jsonify({'error': f'Database operation failed: {str(db_exc)}'}), 500

        return jsonify(answer)

    except Exception as e:
        # Этот блок теперь будет ловить ошибки, не связанные с внешним API или БД (например, проблемы с get_json)
        # Ошибки БД и API обрабатываются в своих try-except блоках.
        # Однако, если db.session.rollback() не был вызван выше, он должен быть здесь.
        # Но т.к. мы его вызываем в блоке db_exc, здесь это может быть излишне или даже вредно, если сессия уже откачена.
        # db.session.rollback() # Будьте осторожны с двойным rollback
        logging.error(f'Generic error in /gen_presentation_by_title: {str(e)}', exc_info=True)
        return jsonify({'error': f'An internal error occurred: {str(e)}'}), 500
    # finally:
        # Flask-SQLAlchemy сама управляет закрытием сессии в конце запроса, явный close не нужен.
        # db.session.close()
        # logging.debug('Database session closed by Flask-SQLAlchemy (implicitly)')

@api_bp.route('/gen_presentation_by_text', methods=['POST'])
def gen_presentation_by_text():
    logging.debug('Starting /gen_presentation_by_text')
    try:
        data = request.get_json()
        if not data:
            logging.warning('No JSON data provided for /gen_presentation_by_text')
            return jsonify({'error': 'No JSON data provided'}), 400

        name_of_presentation = data.get("Presentation_title", "Untitled Presentation")
        name_of_creator = data.get("user_name", "User_1")

        logging.debug(f'Calling external API for presentation by text: {name_of_presentation}')
        try:
            headers = {"Content-Type": "application/json", "User-Agent": "MyApp"}
            response = requests.post(
                "http://127.0.0.1:5001/api_neuro_part/gen_by_text",
                json=data,
                headers=headers,
                timeout=30000
            )
            response.raise_for_status()
            answer = response.json()
        except requests.RequestException as e:
            logging.error(f'External API error in /gen_presentation_by_text: {str(e)}')
            return jsonify({'error': f'External API error: {str(e)}'}), 500

        presentation = Presentation(
            user_name=name_of_creator,
            name_of_presentation=name_of_presentation,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(presentation)
        db.session.flush()

        slides_data = answer.get('Slides', [])
        for slide_data in slides_data:
            slide = Slide(
                presentation_id=presentation.id,
                theme=slide_data.get('Slide_theme', "Theme_1"),
                title=slide_data.get('Slide_title', 'Untitled Slide'),
                title_font=slide_data.get('Slide_title_font', "Normal"),
                title_font_size=slide_data.get('Slide_title_font_size', 16),
                content=slide_data.get('Slide_content', ''),
                content_font=slide_data.get('Slide_content_font', "Normal"),
                content_font_size=slide_data.get('Slide_content_font_size', 14),
                images=slide_data.get('Slide_images', [])
            )
            db.session.add(slide)

        db.session.commit()
        logging.debug('Database commit successful for /gen_presentation_by_text')
        return jsonify(answer)

    except Exception as e:
        db.session.rollback()
        logging.error(f'Error in /gen_presentation_by_text: {str(e)}', exc_info=True)
        return jsonify({'error': f'An internal error occurred: {str(e)}'}), 500

@api_bp.route('/create_presentation', methods=['POST'])
def create_presentation():
    logging.debug('Starting /create_presentation')
    try:
        data = request.get_json()
        if not data:
            logging.warning('No JSON data provided for /create_presentation')
            return jsonify({'error': 'No JSON data provided'}), 400

        # Используем оригинальные ключи из format.json
        name_of_presentation = data.get('Name of presentation', 'Untitled Presentation')
        user_name = data.get('Name of creator', 'Unknown User')

        presentation = Presentation(
            user_name=user_name,
            name_of_presentation=name_of_presentation,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(presentation)
        db.session.flush()

        slides_data = data.get('slides', [])
        for slide_data in slides_data:
            slide = Slide(
                presentation_id=presentation.id,
                theme=slide_data.get('theme', 'Theme_1'),
                title=slide_data.get('title', 'Untitled Slide'),
                title_font=slide_data.get('title_font', 'Normal'),
                title_font_size=slide_data.get('title_font_size', 16),
                content=slide_data.get('content', ''),
                content_font=slide_data.get('content_font', 'Normal'),
                content_font_size=slide_data.get('content_font_size', 14),
                images=slide_data.get('images_url', []) # Ключ из format.json
            )
            db.session.add(slide)

        db.session.commit()
        logging.debug('Database commit successful for /create_presentation')

        return jsonify({
            'message': 'Presentation created successfully',
            'id': presentation.id,
            'name_of_presentation': presentation.name_of_presentation,
            'user_name': presentation.user_name,
            'slides_count': len(slides_data)
        }), 201

    except Exception as e:
        db.session.rollback()
        logging.error(f'Error in /create_presentation: {str(e)}', exc_info=True)
        return jsonify({'error': f'An internal error occurred: {str(e)}'}), 500

@api_bp.route('/get_presentation/<int:id>', methods=['GET'])
def get_presentation(id):
    logging.debug(f'Starting /get_presentation for id: {id}')
    try:
        presentation = Presentation.query.get_or_404(id)
        slides = Slide.query.filter_by(presentation_id=id).order_by(Slide.id).all()

        return jsonify({
            'id': presentation.id,
            'name_of_presentation': presentation.name_of_presentation, # Имя поля из модели
            'user_name': presentation.user_name, # Имя поля из модели
            'created_at': presentation.created_at.isoformat(),
            'updated_at': presentation.updated_at.isoformat(),
            'slides': [
                {
                    'slide_id': slide.id,
                    'slide_number': index,
                    'theme': slide.theme,
                    'title': slide.title,
                    'title_font': slide.title_font,
                    'title_font_size': slide.title_font_size,
                    'content': slide.content,
                    'content_font': slide.content_font,
                    'content_font_size': slide.content_font_size,
                    'images': slide.images # Имя поля из модели
                } for index, slide in enumerate(slides, start=1)
            ]
        })

    except Exception as e:
        logging.error(f'Error retrieving presentation {id}: {str(e)}', exc_info=True)
        if hasattr(e, 'code') and e.code == 404:
            return jsonify({'error': f'Presentation with id {id} not found'}), 404
        return jsonify({'error': f'Error retrieving presentation: {str(e)}'}), 500

@api_bp.route('/get_presentations_all/<string:user_name>', methods=['GET'])
def get_presentations_all(user_name):
    logging.debug(f'Starting /get_presentations_all for user: {user_name}')
    try:
        presentations_with_counts = db.session.query(
            Presentation, func.count(Slide.id).label('slides_count')
        ).outerjoin(Slide, Presentation.id == Slide.presentation_id)\
         .filter(Presentation.user_name == user_name)\
         .group_by(Presentation.id)\
         .order_by(Presentation.updated_at.desc())\
         .all()

        if not presentations_with_counts:
            logging.info(f'No presentations found for user {user_name}')
            return jsonify({
                'message': f'No presentations found for user {user_name}',
                'presentations': []
            }), 200

        return jsonify({
            'user_name': user_name, # Имя поля из модели
            'presentations': [
                {
                    'id': p.id,
                    'name_of_presentation': p.name_of_presentation, # Имя поля из модели
                    'created_at': p.created_at.isoformat(),
                    'updated_at': p.updated_at.isoformat(),
                    'slides_count': count
                } for p, count in presentations_with_counts
            ]
        })

    except Exception as e:
        logging.error(f'Error retrieving presentations for user {user_name}: {str(e)}', exc_info=True)
        return jsonify({'error': f'Error retrieving presentations: {str(e)}'}), 500