import logging
from io import BytesIO

from flask import Blueprint, request, redirect, jsonify

from open_ai.service import OpenAIService

openai_service = OpenAIService()
file_uploading_blueprint = Blueprint('file_uploading', __name__)


@file_uploading_blueprint.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']
        logging.info(f"Received file: {file}")

        # Common browser error (names empty file if no file is selected)
        if file.filename == '':
            return redirect(request.url)

        if file:
            file_bytes = BytesIO(file.read())
            file_response = openai_service.create_file(file=file_bytes)

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
            # TODO: Save to database, map user to file uploaded

            return jsonify({'data': file_response_dict})
    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500
