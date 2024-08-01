from flask import Flask, request, jsonify, Blueprint
from sqlalchemy.orm import Session
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from db.db_models import User, engine

registration_blueprint = Blueprint('registration', __name__)
login_blueprint = Blueprint('login', __name__)
logout_blueprint = Blueprint('logout', __name__)
protected_blueprint = Blueprint('protected', __name__)


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
    email = request.form.get('email')
    password = request.form.get('password')

    with Session(engine) as db_session:
        user = db_session.query(User).filter_by(email=email).first()

        if user and user.check_password(password):
            # Create a new token with the user id inside
            access_token = create_access_token(identity=user.id)
            return jsonify(access_token=access_token, message="Login successful"), 200
        else:
            return jsonify({'message': 'Invalid username or password'}), 401

@logout_blueprint.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # JWTs are stateless; hence logging out can't actually invalidate the token.
    # You should handle log out on the client side by deleting the stored token.
    # Optionally, maintain a token denylist server-side if necessary.
    user_id = get_jwt_identity()
    return jsonify({'message': f'Successfully logged out user {user_id}'}), 200

@protected_blueprint.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user)