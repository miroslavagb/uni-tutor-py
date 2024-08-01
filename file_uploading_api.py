import logging
from io import BytesIO
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session
from db.db_models import engine, File, User
from open_ai.service import OpenAIService

openai_service = OpenAIService()
file_uploading_blueprint = Blueprint('file_uploading', __name__)
file_retrieving_blueprint = Blueprint('file_retrieving', __name__)

@file_uploading_blueprint.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    current_user_id = get_jwt_identity()
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    if not file.filename.endswith('.pdf'): #only pdf accepted!
        return jsonify({'error': 'Only PDF files are accepted'}), 400

    try:
        file_bytes = BytesIO(file.read())  
        file_response = openai_service.create_file(file=(file.filename, file_bytes))  

        with Session(engine) as db_session:
            new_file = File(
                name=file.filename,
                open_ai_id=file_response.id,
                user_id=current_user_id,  
                status=file_response.status
            )
            db_session.add(new_file)  
            db_session.commit()  
        
        return jsonify({
            'id': file_response.id,
            'bytes': file_response.bytes,
            'created_at': file_response.created_at,
            'filename': file_response.filename,
            'object': file_response.object,
            'purpose': file_response.purpose,
            'status': file_response.status,
            'status_details': file_response.status_details
        })  
    except Exception as e:
        logging.error(f"Failed to upload file: {e}")
        return jsonify({'error': str(e)}), 500  

@file_retrieving_blueprint.route('/retrieve', methods=['GET'])
@jwt_required()
def retrieve_file():
    current_user_id = get_jwt_identity()
    with Session(engine) as db_session:
        user = db_session.query(User).get(current_user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        files = [{
            "id": file.id,
            "name": file.name,
            "status": file.status,
            "open_ai_id": file.open_ai_id
        } for file in user.files]

        return jsonify({'files': files}), 200  #DB list of files with userid
