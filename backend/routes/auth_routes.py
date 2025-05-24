from flask import Blueprint, make_response, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt, jwt_required, get_jwt_identity
from flask_jwt_extended.utils import decode_token
from extensions import bcrypt
from sqlalchemy import func
from controllers.auth_controller import authenticate_user
from models import TokenBlacklist, db, User
from datetime import datetime, timedelta
from models import User
import re

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/api/refresh', methods=['POST'])
def refresh():
    data = request.get_json()
    refresh_token = data.get('refresh_token')

    if not refresh_token:
        return jsonify({"message": "Brak refresh tokenu."}), 400

    try:
        decoded_token = decode_token(refresh_token)
        refresh_jti = decoded_token['jti']
        user_id = decoded_token['sub']
        user = User.query.filter_by(id=user_id).first()

        if not user:
            return jsonify({"message": "Użytkownik nie istnieje."}), 404
        
        blacklisted = TokenBlacklist.query.filter_by(jti=refresh_jti).first()
        if blacklisted:
            return jsonify({"message": "Refresh token unieważniony."}), 401

        access_token_expire = "00:00:10:00"
        access_expires_delta = timedelta(minutes=10)
        refresh_token_expire = "00:01:00:00"
        refresh_expires_delta = timedelta(hours=1)

        access_token = create_access_token(identity=str(user.id), expires_delta=access_expires_delta)
        refresh_token = create_refresh_token(identity=str(user.id), expires_delta=refresh_expires_delta)

        return jsonify({
            "message": "Tokeny odświeżone pomyślnie",
            "username": user.username,
            "email": user.email,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expire_time": str(access_token_expire),
            "refresh_expire_time": str(refresh_token_expire)
        }), 200

    except Exception as e:
        return jsonify({"message": "Błąd podczas odświeżania tokenów: " + str(e)}), 500

@auth_bp.route('/api/logout', methods=['POST'])
@jwt_required()
def logout():
    data = request.get_json()
    refresh_token = data.get('refresh_token')

    if not refresh_token:
        return jsonify({"message": "Brak refresh tokenu."}), 400
    
    try:
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()

        decoded_token = decode_token(refresh_token)
        refresh_jti = decoded_token['jti']
        refresh_user_id = decoded_token['sub']
        refresh_user = User.query.filter_by(id=refresh_user_id).first()

        if not user or not refresh_user:
            return jsonify({"message": "Użytkownik nie istnieje."}), 404
        
        if user != refresh_user:
            return jsonify({"message": "Nieprawidłowe tokeny."}), 404
        
        blacklisted = TokenBlacklist.query.filter_by(jti=refresh_jti).first()
        if blacklisted:
            return jsonify({"message": "Refresh token unieważniony."}), 401
        
        current_token = get_jwt()
        jti = current_token['jti']
        refresh_jti = decoded_token['jti']

        access_expiration = datetime.fromtimestamp(current_token['exp'])
        access_blacklist = TokenBlacklist(
            username=user.username,
            email=user.email,
            jti=jti,
            expires_at=access_expiration
        )

        refresh_expiration = datetime.fromtimestamp(decoded_token['exp'])
        refresh_blacklist = TokenBlacklist(
            username=refresh_user.username,
            email=refresh_user.email,
            jti=refresh_jti,
            expires_at=refresh_expiration
        )

        db.session.add(access_blacklist)
        db.session.add(refresh_blacklist)
        db.session.commit()

        return jsonify({"message": "Wylogowano pomyślnie."}), 200
    except Exception as e:
        return jsonify({"message": "Błąd podczas wylogowania: " + str(e)}), 500

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = authenticate_user(data.get('usernameOrEmail'), data.get('password'))
    if not user:
        return jsonify({"message": "Użytkownik nie istnieje."}), 401
    
    try:
        if not data.get('usernameOrEmail') or not data.get('password'):
            return jsonify({"message": "Brak wymaganych pól: usernameOrEmail, password."}), 400
        if data.get('usernameOrEmail') == '' or data.get('password') == '':
            return jsonify({"message": "Pola usernameOrEmail i password nie mogą być puste."}), 400
        if len(data.get('usernameOrEmail')) < 6 or len(data.get('usernameOrEmail')) > 320 or len(data.get('password')) > 20 or len(data.get('password')) < 8:
            return jsonify({"message": "Pola usernameOrEmail i password nie mogą mieć mniej niż 6, 8 oraz więcej niż 320 i 20 znaków."}), 400
    except (ValueError, TypeError):
        return jsonify({"message": "Nieprawidłowy format danych."}), 400

    if user and bcrypt.check_password_hash(user.password, data.get('password')):
        access_token_expire = "00:00:10:00"
        access_expires_delta = timedelta(minutes=10)
        if data.get('remember'):
            refresh_token_expire = "01:00:00:00"
            refresh_expires_delta = timedelta(days=1)
        else:
            refresh_token_expire = "00:01:00:00"
            refresh_expires_delta = timedelta(hours=1)

        access_token = create_access_token(identity=str(user.id), expires_delta=access_expires_delta)
        refresh_token = create_refresh_token(identity=str(user.id), expires_delta=refresh_expires_delta)

        response = make_response(jsonify({
            "message": "Logowanie pomyślne",
            "username": user.username,
            "email": user.email,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expire_time": str(access_token_expire),
            "refresh_expire_time": str(refresh_token_expire)
        }))

        return response, 200

    return jsonify({"message": "Niepoprawne dane."}), 401

@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    try:
        polish_chars = r"[ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]"

        if not data.get('username') or not data.get('email') or not data.get('password') or not data.get('password2'):
            return jsonify({"message": "Brak wymaganych pól: username, email, password, password2."}), 400
        if data.get('username') == '' or data.get('email') == '' or data.get('password') == '' or data.get('password2') == '':
            return jsonify({"message": "Pola username, email, password i password2 nie mogą być puste."}), 400
        if len(data.get('username')) < 5 or len(data.get('username')) > 20 or len(data.get('email')) < 6 or len(data.get('email')) > 320 or len(data.get('password')) > 20 or len(data.get('password')) < 8:
            return jsonify({"message": "Pola username, email i password nie mogą mieć mniej niż 5, 6 i 8 oraz więcej niż 20, 320 i 20 znaków."}), 400
        if " " in data.get('username') or " " in data.get('email') or " " in data.get('password') or " " in data.get('password2'):
            return jsonify({"message": "Pola username, email, password i password2 nie mogą zawierać spacji."}), 400
        if re.search(polish_chars, data.get('username')):
            return jsonify({"message": "Nazwa użytkownika nie może zawierać polskich znaków."}), 400
        if re.search(polish_chars, data.get('email')):
            return jsonify({"message": "Email nie może zawierać polskich znaków."}), 400
        if re.search(polish_chars, data.get('password')):
            return jsonify({"message": "Hasło nie może zawierać polskich znaków."}), 400
        if not re.match(r"[^@]+@[^@]+\.[^@]+", data.get('email')):
            return jsonify({"message": "Nieprawidłowy format adresu email."}), 400
        if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?\":{}|<>[\]])[A-Za-z\d!@#$%^&*(),.?\":{}|<>[\]]{8,20}$", data.get('password')):
            return jsonify({"message": "Hasło musi mieć co najmniej jedną małą literę, jedną wielką literę, jedną cyfrę i jeden znak specjalny."}), 400
        if data.get('password') != data.get('password2'):
            return jsonify({"message": "Hasła nie są zgodne."}), 400
    except (ValueError, TypeError):
        return jsonify({"message": "Nieprawidłowy format danych."}), 400

    if User.query.filter(func.lower(User.username) == data.get('username').lower()).first():
        return jsonify({"message": "Nazwa użytkownika jest już zajęta."}), 400
    
    if User.query.filter(func.lower(User.email) == data.get('email').lower()).first():
        return jsonify({"message": "Email jest już zajęty."}), 400

    hashed_password = bcrypt.generate_password_hash(data.get('password')).decode('utf-8')

    new_user = User(username=data.get('username'), email=data.get('email'), password=hashed_password)

    try:
        db.session.add(new_user)
        db.session.commit()

       
        access_token_expire = "00:00:10:00"
        access_expires_delta = timedelta(minutes=10)
        refresh_token_expire = "00:01:00:00"
        refresh_expires_delta = timedelta(hours=1)

        access_token = create_access_token(identity=str(new_user.id), expires_delta=access_expires_delta)
        refresh_token = create_refresh_token(identity=str(new_user.id), expires_delta=refresh_expires_delta)

        response = make_response(jsonify({
            "message": "Rejestracja pomyślna",
            "username": new_user.username,
            "email": new_user.email,
            "access_token": str(access_token),
            "refresh_token": str(refresh_token),
            "expire_time": str(access_token_expire),
            "refresh_expire_time": str(refresh_token_expire)
        }))

        return response, 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Błąd podczas rejestracji: " + str(e)}), 500

@auth_bp.route('/api/clear-session', methods=['GET'])
def clear_session():
    response = make_response(jsonify({"message": "Ciasteczko 'session' usunięte."}))
    response.delete_cookie("session")
    return response, 200