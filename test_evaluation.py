import json
import os

from flask import Blueprint, jsonify, request
from db.db_models import Question, Option, engine, User

from sqlalchemy.orm import Session

from open_ai.service_facade import OpenAIServiceFacade

test_evaluation_blueprint = Blueprint('test_evaluation', __name__)

EVALUATING_ASSISTANT = os.getenv('EVALUATING_ASSISTANT')
openai_facade = OpenAIServiceFacade()


@test_evaluation_blueprint.route('/evaluate', methods=['POST'])
def evaluate_test():
    user_id = request.headers.get('User-Id')
    file_id = request.headers.get('File-Id')

    if user_id is None:
        return jsonify({'error': 'You should first log in in order to upload a file'}), 401
    if file_id is None:
        return jsonify({'error': 'You should select a file for asking questions'}), 400

    user_answers = request.json.get(
        'answers')  # TODO {"answers": [{"question_id": "..", "option_id": ".."}, ...]}

    with Session(engine) as session:
        user = session.query(User).get(user_id)
        if user is None:
            return jsonify({'error': 'User not found'}), 401

        file = next((f for f in user.files if str(f.id) == file_id), None)
        if file is None:
            return jsonify({'error': 'File not found or access denied'}), 403
        
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
            # TODO: Add other fields as needed
        }
        serialized_data.append(message_info)

    return serialized_data
