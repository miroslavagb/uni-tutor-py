import logging

from flask import Blueprint, jsonify, request
import question_generating_service

question_generating_blueprint = Blueprint('question_generating', __name__)


@question_generating_blueprint.route('/generate/<int:question_count>', methods=['POST'])
def generate_questions(question_count):
    try:
        file_ids = request.args.getlist('file_id')
        additional_prompt = request.form.get('prompt', '')
        question_theme = request.form['theme']
        questions = question_generating_service.generate_questions(question_count, file_ids, question_theme,
                                                                   additional_prompt)
        return jsonify({'data': questions})
    except Exception as e:
        logging.error(f"Error occurred during generating questions: {e}")
        return jsonify({'error': str(e)}), 500
