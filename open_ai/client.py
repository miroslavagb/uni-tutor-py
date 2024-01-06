import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv('app_variables.env')

class OpenAIClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OpenAIClient, cls).__new__(cls)
            cls._instance.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        return cls._instance
