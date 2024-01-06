from flask import Blueprint, jsonify, request

from question_generating_service import generate_questions

question_generating_blueprint = Blueprint('question_generating', __name__)


@question_generating_blueprint.route('/generate/<int:question_count>', methods=['POST'])
def generate_question(question_count):
    try:
        file_ids = request.args.getlist('file_id')
        questions = generate_questions(question_count, file_ids)
        return jsonify({'data': questions})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
