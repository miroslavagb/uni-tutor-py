from flask import Blueprint, jsonify, request
from db.db_models import Question, Option, engine
from sqlalchemy.orm import Session

test_evaluation_blueprint = Blueprint('test_evaluation', __name__)


@test_evaluation_blueprint.route('/evaluate', methods=['POST'])
def evaluate_test():
    user_answers = request.json.get(
        'answers')  # TODO {"answers": [{"question_id": "..", "option_id": ".."}, ...]}

    with Session(engine) as session:
        incorrect_answers = []

        for answer in user_answers:
            question = session.query(Question).get(answer['question_id'])
            selected_option = session.query(Option).get(answer['option_id'])

            if not selected_option.is_correct:
                incorrect_answers.append({
                    "question_id": question.id,
                    "question_title": question.title,
                    "answer_description": question.answer_description
                    # TODO: Add selected_option and the correct option itself. + Question Difficulty?
                })

                # TODO: [OPTIONAL] Apply GPT feedback/report based on answers provided by user

    return jsonify({"incorrect_answers": incorrect_answers})
