import os

from open_ai.service_facade import OpenAIServiceFacade

QUESTION_GENERATING_ASSISTANT = os.getenv('QUESTION_GENERATING_ASSISTANT')
openai_facade = OpenAIServiceFacade()


def generate_questions(question_count, file_ids):
    content = f"Generate {question_count} questions about files with id: {file_ids}"
    questions = openai_facade.execute_run(content=content, assistant_id=QUESTION_GENERATING_ASSISTANT,
                                          file_ids=file_ids)
    # TODO: Parse questions to some understandable format
    return questions
