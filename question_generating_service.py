import logging
import os
import json
from db.db_models import engine, Question, Option, Difficulty
from open_ai.service_facade import OpenAIServiceFacade
from sqlalchemy.orm import Session

QUESTION_GENERATING_ASSISTANT = os.getenv('QUESTION_GENERATING_ASSISTANT')
openai_facade = OpenAIServiceFacade()


# TODO If I have question generating assistant, and then I fetch the questions in string format and pass them to a second "String to JSON coverter" assistant. ?

def generate_questions(question_count, file_ids, question_theme, additional_prompt):
    content = (f"Generate {question_count} new questions about {question_theme}. Return "
               f"response only in the desired JSON format. (generatedQuestions list). IMPORTANT NOTE: Generate a "
               f"'generatedQuestions' json response and don't respond with any other additional word. "
               f"{additional_prompt}")

    logging.info(f"Sending prompt with content: {content}")
    questions = openai_facade.execute_run(content=content, assistant_id=QUESTION_GENERATING_ASSISTANT,
                                          file_ids=file_ids)
    logging.info(f"Successfully generated questions: {questions}")

    response_json = serialize_thread_messages(questions)
    generated_questions_data = parse_generated_questions(response_json)

    if 'error' in generated_questions_data:
        return generated_questions_data

    return save_questions_to_database(generated_questions_data)


def serialize_thread_messages(sync_cursor_page):
    serialized_data = []
    for thread_message in sync_cursor_page.data:
        for content in thread_message.content:
            if hasattr(content, 'text') and hasattr(content.text, 'value'):
                message_info = {
                    'id': thread_message.id,
                    'content': content.text.value.strip(),
                }
                serialized_data.append(message_info)
    return serialized_data


def parse_generated_questions(response_json):
    generated_questions_data = []
    for item in response_json:
        if 'content' in item:
            try:
                # Check if content is JSON
                cleaned_json_str = item['content']
                cleaned_json_str = cleaned_json_str.replace('```json\n', '').replace('\n```', '').replace('\\n', '').replace("\\'", "'").replace('\\"', '"')
                logging.info(f"Attempting to parse JSON: {cleaned_json_str}")
                parsed_data = json.loads(cleaned_json_str)

                if 'generatedQuestions' in parsed_data:
                    generated_questions_data.extend(parsed_data['generatedQuestions'])
            except json.JSONDecodeError as e:
                logging.error(f"JSON parsing error: {e}")
                logging.error(f"Failed to parse string: {cleaned_json_str}")
                continue  # Skip to the next item if parsing fails

    if not generated_questions_data:
        return {"error": "No valid JSON found"}

    print(f"GENERATED QUESTIONS: {generated_questions_data}")
    return generated_questions_data


def save_questions_to_database(generated_questions_data):
    with Session(engine) as session:
        response_questions = []
        for question_data in generated_questions_data:
            question = Question(
                title=question_data['title'],
                difficulty=question_data['difficulty'],
                answer_description=question_data['answerDescription'],
                source_page=question_data['page']
            )

            for option_data in question_data['options']:
                option = Option(
                    key=list(option_data.keys())[0],  # The key is the first key in the option_data dictionary
                    value=option_data[list(option_data.keys())[0]],  # The value is the text associated with the key
                    is_correct=option_data['isCorrect']
                )
                question.options.append(option)

            session.add(question)
            session.flush()  # Assigns an ID to the question and its options

            response_question = {
                "id": question.id,
                "title": question.title,
                "options": [{"id": option.id, "key": option.key, "value": option.value} for option in question.options]
            }
            response_questions.append(response_question)
            session.commit()

        return {"questions": response_questions}
