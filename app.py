import logging

from dotenv import load_dotenv
from flask import Flask

load_dotenv('app_variables.env')


def create_app():
    return Flask(__name__)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app = create_app()
    app.run(debug=True)
