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

        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            return redirect(request.url)

        if file:
            file_response = openai_service.create_file(file=file)
            return jsonify({'data': file_response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
