from flask import Blueprint, jsonify, request
from db.db_models import Question, Option, engine
from sqlalchemy.orm import Session

test_evaluation_blueprint = Blueprint('test_evaluation', __name__)


@test_evaluation_blueprint.route('/evaluate', methods=['POST'])
def evaluate_test():
    user_answers = request.json.get(
        'answers')  # TODO {"answers": [{"question_id": "..", "option_id": ".."}, ...]}

    with Session(engine) as session:
        evaluation_response = []

        for answer in user_answers:
            question = session.query(Question).get(answer['question_id'])
            selected_option = session.query(Option).get(answer['option_id'])
            correct_option = session.query(Option).filter_by(question_id=question.id, is_correct=True).first()

            evaluation_response.append({
                "question_id": question.id,
                "question_title": question.title,
                "answer_description": question.answer_description,
                "selected_option": serialize_option(selected_option),
                "correct_option": serialize_option(correct_option)
                # TODO: Add selected_option and the correct option itself. + Question Difficulty?
            })

            # TODO: [OPTIONAL] Apply GPT feedback/report based on answers provided by user

    return jsonify({"evaluation_response": evaluation_response})


def serialize_option(option):
    return {
        "key": option.key,
        "value": option.value,
    }
