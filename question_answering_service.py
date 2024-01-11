import os
from open_ai.service_facade import OpenAIServiceFacade

QUESTION_ANSWERING_ASSISTANT = os.getenv('QUESTION_ANSWERING_ASSISTANT')
openai_facade = OpenAIServiceFacade()


def answer_question(question, file_ids):
    answer = openai_facade.execute_run(content=question, assistant_id=QUESTION_ANSWERING_ASSISTANT,
                                       file_ids=file_ids)
    # TODO: Parse answer to some understandable format (Currently will return the whole response object)
    return answer
