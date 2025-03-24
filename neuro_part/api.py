from flask import Blueprint, request, jsonify
from json_handler import parse_json_with_def_params, parse_json_with_text

api_bp = Blueprint('api_neuro_part', __name__)

@api_bp.route('/gen_by_def_params', methods = ['POST'])
def gen_by_def_params():
    data = request.get_json()
    parse_json_with_def_params(data)
    return jsonify({
        'massage': 'Богдан бусинка, все воркает)). Дефолтные параметры передались.'
    })

@api_bp.route('/gen_by_text', methods = ['POST'])
def gen_by_text():
    data = request.get_json()
    parse_json_with_text(data)
    return jsonify({
        'massage': 'Богдан бусинка, все воркает)). Текст передался'
    })