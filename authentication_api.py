# Re-running the necessary code after execution state reset
from flask import Flask, request, jsonify, Blueprint, session
from sqlalchemy.orm import Session

from db.db_models import User, engine

registration_blueprint = Blueprint('registration', __name__)
login_blueprint = Blueprint('login', __name__)
logout_blueprint = Blueprint('logout', __name__)


@registration_blueprint.route('/registration', methods=['POST'])
def register():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    confirm_password = request.form.get('confirmPassword')

    if password != confirm_password:
        return jsonify({'message': 'Passwords do not match'}), 400

    with Session(engine) as db_session:
        existing_user = db_session.query(User).filter_by(email=email).first()

        if existing_user:
            return jsonify({'message': 'Email already registered'}), 400

        new_user = User(email=email, name=name)
        new_user.set_password(password)

        db_session.add(new_user)
        db_session.commit()

    return jsonify({'message': 'User registered successfully'}), 201


@login_blueprint.route('/login', methods=['POST'])
def login():
    with Session(engine) as db_session:
        user = db_session.query(User).filter_by(email=request.form.get('email')).first()

    if user and user.check_password(request.form.get('password')):
        #session['user_id'] = user.id
        response = jsonify({'message': 'Login successful'})
        response.headers['user_id'] = user.id
        return response, 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401


@logout_blueprint.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Successfully logged out'}), 200
