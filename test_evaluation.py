import json
import os
from flask import Blueprint, jsonify, request
from sqlalchemy.orm import Session
from db.db_models import Question, Option, User, engine, File  
from flask_jwt_extended import jwt_required, get_jwt_identity
from open_ai.service_facade import OpenAIServiceFacade
import logging

test_evaluation_blueprint = Blueprint('test_evaluation', __name__)
EVALUATING_ASSISTANT = os.getenv('EVALUATING_ASSISTANT')
openai_facade = OpenAIServiceFacade()

@test_evaluation_blueprint.route('/evaluate', methods=['POST'])
@jwt_required()
def evaluate_test():
    user_id = get_jwt_identity()
    file_id = request.headers.get('File-ID')  

    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    if not file_id:
        return jsonify({'error': 'File ID is required for evaluation'}), 400

    with Session(engine) as session:
        user = session.query(User).get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        logging.debug(f"User ID: {user_id}, File ID: {file_id}")
        logging.debug(f"Files available for user: {[f.open_ai_id for f in user.files]}")

    
        file = next((f for f in user.files if f.open_ai_id == file_id), None)
        if not file:
            return jsonify({'error': 'File not found or access denied'}), 403

        user_answers = request.json.get('userAnswers', [])
        evaluation_response = []

        for answer in user_answers:
            question = session.query(Question).get(answer['question_id'])
            selected_option = session.query(Option).get(answer['option_id'])
            correct_option = session.query(Option).filter_by(question_id=question.id, is_correct=True).first()

            evaluation_response.append({
                "question_id": question.id,
                "question_title": question.title,
                "question_difficulty": question.difficulty,
                "question_source_page": question.source_page,
                "answer_description": question.answer_description,
                "selected_option": serialize_option(selected_option),
                "correct_option": serialize_option(correct_option)
            })

        evaluation_response_json = json.dumps({"evaluation_response": evaluation_response})
        answer = openai_facade.execute_run(content=evaluation_response_json, file_ids=[file.open_ai_id], assistant_id=EVALUATING_ASSISTANT)
        serialized_answer = serialize_thread_messages(answer)[0]

        return jsonify({"evaluation_response": serialized_answer})

def serialize_option(option):
    if not option:
        return None
    return {
        "key": option.key,
        "value": option.value,
    }

def serialize_thread_messages(sync_cursor_page):
    serialized_data = []
    for thread_message in sync_cursor_page.data:
        concatenated_values = ''
        for content in thread_message.content:
            if hasattr(content, 'text') and hasattr(content.text, 'value'):
                concatenated_values += content.text.value + ' '

        message_info = {
            'id': thread_message.id,
            'content': concatenated_values.strip(),
        }
        serialized_data.append(message_info)

    return serialized_data
