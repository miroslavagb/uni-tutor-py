import logging
from io import BytesIO
from typing import Tuple

from flask import Blueprint, request, redirect, jsonify
from sqlalchemy.orm import Session

from db.db_models import engine, File, User
from open_ai.service import OpenAIService

openai_service = OpenAIService()
file_uploading_blueprint = Blueprint('file_uploading', __name__)
file_retrieving_blueprint = Blueprint('file_retrieving', __name__)


@file_uploading_blueprint.route('/upload', methods=['POST'])
def upload_file():
    user_id = request.headers.get('User-Id')
    if user_id is None:
        return jsonify({'error': 'You should first log in in order to upload a file'}), 401
    try:
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']
        logging.info(f"Received file: {file}, name: {file.filename}")

        # Common browser error (names empty file if no file is selected)
        if file.filename == '':
            return redirect(request.url)

        if file:
            file_bytes = BytesIO(file.read())
            file_response = openai_service.create_file(file=(file.filename, file_bytes))

            file_response_dict = {
                'id': file_response.id,
                'bytes': file_response.bytes,
                'created_at': file_response.created_at,
                'filename': file_response.filename,
                'object': file_response.object,
                'purpose': file_response.purpose,
                'status': file_response.status,
                'status_details': file_response.status_details
            }

            with Session(engine) as db_session:
                file_entity = File(
                    name=file_response_dict['filename'],
                    open_ai_id=file_response_dict['id'],
                    status=file_response_dict['status'],
                )

                file_entity.user = db_session.query(User).get(user_id)

                db_session.add(file_entity)
                db_session.commit()

            return jsonify({'data': file_response_dict})
    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500


@file_retrieving_blueprint.route('/retrieve', methods=['GET'])
def retrieve_file():
    user_id = request.headers.get('User-Id')
    if user_id is None:
        return jsonify({'error': 'You should first log in in order to retrieve files'}), 401

    with Session(engine) as db_session:
        user = db_session.query(User).get(user_id)
        if user is None:
            return jsonify({'error': 'User not found'}), 401

        files_data = [
            {
                "id": file.id,
                "name": file.name,
                "status": file.status,
                "open_ai_id": file.open_ai_id
            } for file in user.files
        ]

        return jsonify({'data': files_data})
