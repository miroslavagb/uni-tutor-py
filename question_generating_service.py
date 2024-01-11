import logging
import os

from db.db_models import engine, Question, Option
from open_ai.service_facade import OpenAIServiceFacade
from sqlalchemy.orm import Session

QUESTION_GENERATING_ASSISTANT = os.getenv('QUESTION_GENERATING_ASSISTANT')
openai_facade = OpenAIServiceFacade()


def generate_questions(question_count, file_ids):
    content = f"Generate {question_count} questions about the file: EN_Business-Guide-2020_English_web.pdf"
    logging.info(f"Sending prompt with content: {content}")
    questions = openai_facade.execute_run(content=content, assistant_id=QUESTION_GENERATING_ASSISTANT,
                                          file_ids=file_ids)
    # TODO: Parse questions to some understandable format
    logging.info(f"Successfully generated questions: {questions}")

    with Session(engine) as session:
        response_questions = []

        for question_data in questions:
            question = Question(
                title=question_data['title'],
                difficulty=question_data['difficulty'],
                answer_description=question_data['answerDescription']
            )

            for option_data in question_data['options']:
                option = Option(
                    title=option_data.get('a', option_data.get('b', option_data.get('c', option_data.get('d')))),
                    is_correct=option_data['isCorrect']
                )

                question.options.append(option)
            session.add(question)
            session.flush()  # This will assign an ID to the question and its options

            # Construct the response format
            response_question = {
                "id": question.id,
                "title": question.title,
                "options": [{"id": option.id, "title": option.title} for option in question.options]
            }
            response_questions.append(response_question)

        session.commit()

        # Return the formatted questions
    return {"questions": response_questions}

