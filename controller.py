from flask import Flask, request, jsonify
from sqlalchemy.orm import Session
from db_models import engine, Question, Option
from question_generator import create_run

app = Flask(__name__)


@app.route('/generate/<question_count>', methods=['POST'])
def generate_questions(question_count):
    print(f"Starting generating {question_count} questions")
    try:
        generated_questions = create_run(question_count)
        print(f"Received questions: {generated_questions}")

        # Create a new SampleData instance

        with Session(engine) as session:

            # Assuming `json_data` is the JSON you provided
            for question_data in generated_questions:
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

            session.commit()
            session.close()

        return jsonify({'message': 'Data saved successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


app.run(debug=True)
