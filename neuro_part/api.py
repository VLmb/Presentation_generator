from flask import Blueprint, request, jsonify
from json_handler import neuro_gen_by_params, neuro_gen_by_file
from flask.wrappers import Response  # нужно лишь для того, чтобы показать, что возвращают endpoint-ы

api_bp = Blueprint('api_neuro_part', __name__)


@api_bp.route('/gen_by_def_params', methods=['POST'])
def gen_by_def_params() -> Response:
    """
    Endpoint, что получает json с бэка, после парсит его и отправляет на генерацию
    презентации по заданным параметрам
    :return: json на бэк
    """
    data = request.get_json()
    answer = neuro_gen_by_params(data)
    return jsonify(answer)


@api_bp.route('/gen_by_text', methods=['POST'])
def gen_by_text() -> Response:
    """
    Endpoint, что получает json с бэка, после парсит его и отправляет на генерацию
    презентации по информации, полученной с файла, что приложил пользователь
    :return: json на бэк
    """
    data = request.get_json()
    answer = neuro_gen_by_file(data)
    return jsonify(answer)
