from flask import Blueprint, jsonify, request

import question_answering_service

question_answering_blueprint = Blueprint('question_answering', __name__)


@question_answering_blueprint.route('/answer/<file_id>', methods=['POST'])
def answer_question(file_id):
    try:
        question = request.data
        answer = question_answering_service.answer_question(question, file_id)
        return jsonify({'data': answer})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
