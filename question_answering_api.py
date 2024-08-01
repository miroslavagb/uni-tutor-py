import logging
from flask import Blueprint, jsonify, request
from sqlalchemy.orm import Session
from db.db_models import engine, User, MessagesHistory, File
from flask_jwt_extended import jwt_required, get_jwt_identity
import question_answering_service

question_answering_blueprint = Blueprint('question_answering', __name__)
messages_history_blueprint = Blueprint('messages_history', __name__)

@question_answering_blueprint.route('/answer', methods=['POST'])
@jwt_required()
def answer_question():
    current_user_id = get_jwt_identity()
    file_id = request.headers.get('File-Id')
    if not file_id:
        logging.error("File ID not provided")
        return jsonify({'error': 'You must select a file for asking questions'}), 400

    with Session(engine) as db_session:
        user = db_session.query(User).get(current_user_id)
        if not user:
            logging.error("User not found: " + str(current_user_id))
            return jsonify({'error': 'User not found'}), 401

        file = db_session.query(File).filter_by(id=file_id, user_id=current_user_id).first()
        if not file:
            logging.error("File not found or access denied for file ID: " + str(file_id))
            return jsonify({'error': 'File not found or access denied'}), 403

        question = request.get_data(as_text=True)  
        if not question:
            logging.error("No question provided")
            return jsonify({'error': 'No question provided'}), 400

        try:
            answer = question_answering_service.answer_question(question, [file.open_ai_id])
            message = MessagesHistory(
                question=question,
                content=answer['content'],
                open_ai_msg_id=answer['id'],
                file_id=file.id,
                user_id=current_user_id
            )
            db_session.add(message)
            db_session.commit()
            return jsonify({'data': answer})
        except Exception as e:
            logging.error(f"Failed to process question: {str(e)}")
            return jsonify({'error': 'Failed to process question'}), 500

@messages_history_blueprint.route('/history', methods=['GET'])
@jwt_required()
def get_message_history():
    current_user_id = get_jwt_identity()
    with Session(engine) as db_session:
        user = db_session.query(User).get(current_user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 401

        messages_data = [{
            "id": message.id,
            "question": message.question,
            "content": message.content,
            "file_name": message.file.name
        } for message in user.messages]
        
        return jsonify({'data': messages_data})
