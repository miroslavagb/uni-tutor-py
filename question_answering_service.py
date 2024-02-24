import logging
import os
from open_ai.service_facade import OpenAIServiceFacade

QUESTION_ANSWERING_ASSISTANT = os.getenv('QUESTION_ANSWERING_ASSISTANT')
openai_facade = OpenAIServiceFacade()


def answer_question(question, file_ids):
    answer = openai_facade.execute_run(content=question, assistant_id=QUESTION_ANSWERING_ASSISTANT,
                                       file_ids=file_ids)
    serialized_answer = serialize_thread_messages(answer)
    return serialized_answer[0]


def serialize_thread_messages(sync_cursor_page):
    serialized_data = []
    for thread_message in sync_cursor_page.data:
        concatenated_values = ''
        for content in thread_message.content:
            if hasattr(content, 'text') and hasattr(content.text, 'value'):
                concatenated_values += content.text.value + ' '

        logging.info(f"THREAD: {thread_message}")
        message_info = {
            'id': thread_message.id,
            'content': concatenated_values.strip(),
            # TODO: Add other fields as needed
        }
        serialized_data.append(message_info)

    return serialized_data


