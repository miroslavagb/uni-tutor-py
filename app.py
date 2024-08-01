import logging
from dotenv import load_dotenv
from flask import Flask, jsonify
load_dotenv(dotenv_path='app_variables.env', verbose=True)
from db.db_models import initiate_database
from file_uploading_api import file_uploading_blueprint, file_retrieving_blueprint
from question_answering_api import question_answering_blueprint, messages_history_blueprint
from question_generating_api import question_generating_blueprint
from test_evaluation import test_evaluation_blueprint
from authentication_api import registration_blueprint, login_blueprint, logout_blueprint, protected_blueprint
from flask_cors import CORS
from flask_jwt_extended import JWTManager  


def create_app():
    flask_app = Flask(__name__)
    flask_app.config['JWT_SECRET_KEY'] = 'secret123'  # SECRET KEY SPECIALLY FOR JWT
    jwt = JWTManager(flask_app)

    flask_app.register_blueprint(question_generating_blueprint)
    flask_app.register_blueprint(question_answering_blueprint)
    flask_app.register_blueprint(file_uploading_blueprint)
    flask_app.register_blueprint(test_evaluation_blueprint)
    flask_app.register_blueprint(registration_blueprint)
    flask_app.register_blueprint(login_blueprint)
    flask_app.register_blueprint(logout_blueprint)
    flask_app.register_blueprint(messages_history_blueprint)
    flask_app.register_blueprint(file_retrieving_blueprint)
    flask_app.register_blueprint(protected_blueprint)


    CORS(flask_app)

    @flask_app.errorhandler(Exception)
    def handle_exception(e):
        response = jsonify(message=str(e))
        response.status_code = 500
        return response

    return flask_app

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app = create_app()
    initiate_database()

    app.config['SECRET_KEY'] = 'secret'  # This is Flask's secret, different from JWT's
    app.run(debug=True)