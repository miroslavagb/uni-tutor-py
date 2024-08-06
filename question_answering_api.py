import logging
from flask import Blueprint, jsonify, request
from sqlalchemy.orm import Session
from flask_jwt_extended import jwt_required, get_jwt_identity

import question_answering_service
from db.db_models import engine, User, MessagesHistory, File

question_answering_blueprint = Blueprint('question_answering', __name__)
messages_history_blueprint = Blueprint('messages_history', __name__)

@question_answering_blueprint.route('/answer', methods=['POST'])
def answer_question():
    user_id = request.headers.get('User-Id')
    file_id = request.headers.get('File-Id')

    if not user_id:
        return jsonify({'error': 'You should first log in in order to upload a file'}), 401
    if not file_id:
        return jsonify({'error': 'You should select a file for asking questions'}), 400

    question = request.get_json().get('question', '')
    if not question:
        return jsonify({'error': 'No question provided'}), 400

    with Session(engine) as db_session:
        user = db_session.query(User).get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 401

        file = next((f for f in user.files if str(f.open_ai_id) == file_id), None)

        if not file:
            return jsonify({'error': 'File not found or access denied'}), 403

        try:
            logging.info(f"Received question for file: '{file.name}'. Question: {question}")
            answer = question_answering_service.answer_question(question, file.open_ai_id)

            message = MessagesHistory(
                question=question,
                content=answer['content'],
                open_ai_msg_id=answer['id'],
                file_id=file.id,
                user_id=user.id
            )

            db_session.add(message)
            db_session.commit()

            return jsonify({'data': answer})
        except Exception as e:
            logging.error(f"Error occurred during answering a question: {e}")
            return jsonify({'error': str(e)}), 500
        
@messages_history_blueprint.route('/history', methods=['GET'])
@jwt_required()
def get_message_history():
    current_user_id = get_jwt_identity()
    with Session(engine) as db_session:
        user = db_session.query(User).get(current_user_id)
        if user is None:
            return jsonify({'error': 'User not found'}), 401

        messages_data = [
            {
                "id": message.id,
                "question": message.question,
                "content": message.content,
                "file_name": message.file.name
            } for message in user.messages
        ]

        return jsonify({'data': messages_data})
