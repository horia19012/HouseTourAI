from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token

from db import SessionLocal
from models.user import User

bcrypt = Bcrypt()


def register_user(data):
    db = SessionLocal()
    try:
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        if not name or not email or not password:
            return {'error': 'All fields are required'}, 400

        existing_user = db.query(User).filter_by(email=email).first()
        if existing_user:
            return {'error': 'User already exists'}, 400

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(name=name, email=email, password=hashed_pw)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {'message': 'User registered successfully', 'user_id': new_user.id}, 200

    except Exception as e:
        return {'error': f'Registration failed: {str(e)}'}, 500
    finally:
        db.close()


def authenticate_user(data):
    db = SessionLocal()
    try:
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return {'error': 'Email and password are required'}, 400

        user = db.query(User).filter(User.email == email).first()
        if not user or not bcrypt.check_password_hash(user.password, password):
            return {'error': 'Invalid credentials'}, 401

        access_token = create_access_token(identity=str(user.id))
        return {
            'message': 'Login successful',
            'token': access_token,
            'user_id': user.id
        }, 200

    except Exception as e:
        return {'error': f'Login failed: {str(e)}'}, 500

    finally:
        db.close()
