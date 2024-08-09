import logging
from flask import Blueprint, jsonify, request
import question_generating_service

question_generating_blueprint = Blueprint('question_generating', __name__)

@question_generating_blueprint.route('/generate/<int:question_count>', methods=['POST'])
def generate_questions(question_count):
    try:
        file_ids = request.json.get('file_ids', [])  # Expect file_ids in JSON payload
        additional_prompt = request.json.get('prompt', '')
        question_theme = request.json.get('theme', '')

        if not file_ids:
            return jsonify({'error': 'No file IDs provided'}), 400
        if not question_theme:
            return jsonify({'error': 'No theme provided'}), 400

        questions = question_generating_service.generate_questions(
            question_count,
            file_ids,
            question_theme,
            additional_prompt
        )
        return jsonify({'data': questions})
    except Exception as e:
        logging.error(f"Error occurred during generating questions: {e}")
        return jsonify({'error': str(e)}), 500
