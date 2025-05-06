from flask import Blueprint, request, jsonify
from json_handler import neuro_gen_by_def_params, neuro_gen_by_text

api_bp = Blueprint('api_neuro_part', __name__)

@api_bp.route('/gen_by_def_params', methods = ['POST'])
def gen_by_def_params():
    data = request.get_json()
    answer = neuro_gen_by_def_params(data)
    return jsonify(answer)

@api_bp.route('/gen_by_text', methods = ['POST'])
def gen_by_text():
    data = request.get_json()
    answer = neuro_gen_by_text(data)
    return jsonify(answer)