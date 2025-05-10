from flask import Blueprint, request, jsonify
from database import Presentation, Slide, db
from datetime import datetime
import requests
import logging
from threading import Lock

# Настройка логирования
logging.basicConfig(
    filename='api.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s'
)

# Блокировка для синхронизации операций с базой данных
db_lock = Lock()

api_bp = Blueprint('api_backend', __name__)

@api_bp.route('/gen_presentation_by_title', methods=['POST'])
def gen_presentation_by_params():
    logging.debug('Starting /gen_presentation_by_title')
    try:
        data = request.get_json()
        if not data:
            logging.error('No JSON data provided')
            return jsonify({'error': 'No JSON data provided'}), 400

        name_of_presentation = data.get("Presentation_title", "Untitled Presentation")
        name_of_creator = "User_1"

        logging.debug(f'Calling external API for presentation: {name_of_presentation}')
        try:
            headers = {"Content-Type": "application/json", "User-Agent": "MyApp"}
            response = requests.post(
                "http://127.0.0.1:5001/api_neuro_part/gen_by_def_params",
                json=data,
                headers=headers,
                timeout=60
            )
            response.raise_for_status()
            answer = response.json()
        except requests.RequestException as e:
            logging.error(f'External API error: {str(e)}')
            return jsonify({'error': f'External API error: {str(e)}'}), 500

        with db_lock:
            logging.debug('Acquired db_lock for database operation')
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
                    theme="Theme_1",
                    title=slide_data.get('Slide_title', 'Untitled'),
                    title_font="Normal",
                    title_font_size=16,
                    content=slide_data.get('Slide_content', ''),
                    content_font="Normal",
                    content_font_size=14,
                    images=[]
                )
                db.session.add(slide)

            db.session.commit()
            logging.debug('Database commit successful')

        return jsonify(answer)

    except Exception as e:
        db.session.rollback()
        logging.error(f'Database error: {str(e)}')
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        db.session.close()
        logging.debug('Database session closed')

@api_bp.route('/gen_presentation_by_text', methods=['POST'])
def gen_presentation_by_text():
    logging.debug('Starting /gen_presentation_by_text')
    try:
        data = request.get_json()
        if not data:
            logging.error('No JSON data provided')
            return jsonify({'error': 'No JSON data provided'}), 400

        name_of_presentation = data.get("Presentation_title", "Untitled Presentation")
        name_of_creator = "User_1"

        logging.debug(f'Calling external API for presentation: {name_of_presentation}')
        try:
            headers = {"Content-Type": "application/json", "User-Agent": "MyApp"}
            response = requests.post(
                "http://127.0.0.1:5001/api_neuro_part/gen_by_text",
                json=data,
                headers=headers,
                timeout=60
            )
            response.raise_for_status()
            answer = response.json()
        except requests.RequestException as e:
            logging.error(f'External API error: {str(e)}')
            return jsonify({'error': f'External API error: {str(e)}'}), 500

        with db_lock:
            logging.debug('Acquired db_lock for database operation')
            print(1)
            presentation = Presentation(
                user_name=name_of_creator,
                name_of_presentation=name_of_presentation,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(presentation)
            db.session.flush()

            print(2)

            slides_data = answer.get('Slides', [])
            for slide_data in slides_data:
                print(3)
                slide = Slide(
                    presentation_id=presentation.id,
                    theme="Theme_1",
                    title=slide_data.get('Slide_title', 'Untitled'),
                    title_font="Normal",
                    title_font_size=16,
                    content=slide_data.get('Slide_content', ''),
                    content_font="Normal",
                    content_font_size=14,
                    images=[]
                )
                print(4)
                db.session.add(slide)
                print(5)
            print("-------")
            db.session.commit()
            logging.debug('Database commit successful')
            print(6)

        return jsonify(answer)

    except Exception as e:
        db.session.rollback()
        logging.error(f'Database error: {str(e)}')
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        db.session.close()
        logging.debug('Database session closed')

@api_bp.route('/create_presentation', methods=['POST'])
def create_presentation():
    logging.debug('Starting /create_presentation')
    try:
        data = request.get_json()
        if not data:
            logging.error('No JSON data provided')
            return jsonify({'error': 'No JSON data provided'}), 400

        name_of_presentation = data.get('Name of presentation', 'Untitled Presentation')
        user_name = data.get('Name of creator', 'Unknown User')

        with db_lock:
            logging.debug('Acquired db_lock for database operation')
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
                    title=slide_data.get('title', 'Untitled'),
                    title_font=slide_data.get('title_font', 'Normal'),
                    title_font_size=slide_data.get('title_font_size', 16),
                    content=slide_data.get('content', ''),
                    content_font=slide_data.get('content_font', 'Normal'),
                    content_font_size=slide_data.get('content_font_size', 14),
                    images=slide_data.get('images_url', [])
                )
                db.session.add(slide)

            db.session.commit()
            logging.debug('Database commit successful')

        return jsonify({
            'message': 'Presentation created successfully',
            'id': presentation.id,
            'name_of_presentation': presentation.name_of_presentation,
            'user_name': presentation.user_name,
            'slides_count': len(slides_data)
        })

    except Exception as e:
        db.session.rollback()
        logging.error(f'Database error: {str(e)}')
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        db.session.close()
        logging.debug('Database session closed')

@api_bp.route('/get_presentation/<int:id>', methods=['GET'])
def get_presentation(id):
    logging.debug(f'Starting /get_presentation for id: {id}')
    try:
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
                    'title_font_size': slide.title_font_size,
                    'content': slide.content,
                    'content_font': slide.content_font,
                    'content_font_size': slide.content_font_size,
                    'images': slide.images
                } for index, slide in enumerate(slides, start=1)
            ]
        })

    except Exception as e:
        logging.error(f'Error retrieving presentation: {str(e)}')
        return jsonify({'error': f'Error retrieving presentation: {str(e)}'}), 500
    finally:
        db.session.close()
        logging.debug('Database session closed')

@api_bp.route('/get_presentations_all/<string:user_name>', methods=['GET'])
def get_presentations_all(user_name):
    logging.debug(f'Starting /get_presentations_all for user: {user_name}')
    try:
        presentations = Presentation.query.filter_by(user_name=user_name).all()

        if not presentations:
            logging.info(f'No presentations found for user {user_name}')
            return jsonify({
                'message': f'No presentations found for user {user_name}',
                'presentations': []
            }), 404

        return jsonify({
            'user_name': user_name,
            'presentations': [
                {
                    'id': presentation.id,
                    'name_of_presentation': presentation.name_of_presentation,
                    'created_at': presentation.created_at.isoformat(),
                    'updated_at': presentation.updated_at.isoformat(),
                    'slides_count': Slide.query.filter_by(presentation_id=presentation.id).count()
                } for presentation in presentations
            ]
        })

    except Exception as e:
        logging.error(f'Error retrieving presentations: {str(e)}')
        return jsonify({'error': f'Error retrieving presentations: {str(e)}'}), 500
    finally:
        db.session.close()
        logging.debug('Database session closed')