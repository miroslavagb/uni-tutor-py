import logging
from flask import Blueprint, jsonify, request
from sqlalchemy.orm import Session

import question_answering_service
from db.db_models import engine, User, MessagesHistory

question_answering_blueprint = Blueprint('question_answering', __name__)
messages_history_blueprint = Blueprint('messages_history', __name__)


@question_answering_blueprint.route('/answer', methods=['POST'])
def answer_question():
    user_id = request.headers.get('User-Id')
    file_id = request.headers.get('File-Id')
    if user_id is None:
        return jsonify({'error': 'You should first log in in order to upload a file'}), 401
    if file_id is None:
        return jsonify({'error': 'You should select a file for asking questions'}), 400

    with Session(engine) as db_session:
        user = db_session.query(User).get(user_id)
        if user is None:
            return jsonify({'error': 'User not found'}), 401

        file = next((f for f in user.files if str(f.id) == file_id), None)

        if file is None:
            return jsonify({'error': 'File not found or access denied'}), 403

        try:
            question = request.data.decode('utf-8')
            logging.info(f"Received question for file: '{file.name}'. Question: {question}")
            answer = question_answering_service.answer_question(question, [file.open_ai_id])
            # TODO: Make it pass user.files directly, so the users won't have to set file_id header
            # filenames = [file.name for file in user.files]
            # file_open_ai_ids = [file.open_ai_id for file in user.files]

            message = MessagesHistory(
                question=question,
                content=answer['content'],
                open_ai_msg_id=answer['id']
            )
            message.file = file
            message.user = user

            db_session.add(message)
            db_session.commit()

            return jsonify({'data': answer})
        except Exception as e:
            logging.error(f"Error occurred during answering a question: {e}")
            return jsonify({'error': str(e)}), 500


@messages_history_blueprint.route('/history', methods=['GET'])
def answer_question():
    user_id = request.headers.get('User-Id')
    if user_id is None:
        return jsonify({'error': 'You should first log in in order to retrieve message history'}), 401

    with Session(engine) as db_session:
        user = db_session.query(User).get(user_id)
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
