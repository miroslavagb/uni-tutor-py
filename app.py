import logging

from dotenv import load_dotenv
from flask import Flask

from question_answering_api import question_answering_blueprint
from question_generating_api import question_generating_blueprint

load_dotenv('app_variables.env')


def create_app():
    return Flask(__name__)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app = create_app()
    app.register_blueprint(question_generating_blueprint, url_prefix='/generate')
    app.register_blueprint(question_answering_blueprint, url_prefix='/answer')
    app.run(debug=True)
