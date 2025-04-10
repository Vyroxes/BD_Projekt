from flask import Flask, request, jsonify, make_response, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from flask_jwt_extended.utils import decode_token
from flask_cors import CORS
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_discord import DiscordOAuth2Session, requires_authorization, Unauthorized
from datetime import timedelta, datetime, timezone
from sqlalchemy import CheckConstraint, func, Index
from sqlalchemy.exc import IntegrityError
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
import re
import random
import os

load_dotenv(dotenv_path='.env')

app = Flask(__name__)
CORS(app, supports_credentials=True, allow_headers={
    'Authorization'
})

talisman = Talisman(
    app,
    force_https=True,
    frame_options='DENY',
    content_security_policy={
        'default-src': "'self'",
    },
    referrer_policy='strict-origin-when-cross-origin'
)

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["20 per second"],
    storage_uri="memory://"
)

app.config['SERVER_PORT'] = os.getenv('SERVER_PORT')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config["DISCORD_CLIENT_ID"] =  os.getenv('DISCORD_CLIENT_ID')
app.config["DISCORD_CLIENT_SECRET"] = os.getenv('DISCORD_CLIENT_SECRET')
app.config["DISCORD_REDIRECT_URI"] = "http://localhost:5173/api/auth/discord"
app.config["DISCORD_BOT_TOKEN"] = os.getenv('DISCORD_BOT_TOKEN')
app.secret_key = os.getenv('FLASK_SECRET_KEY')
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

discord = DiscordOAuth2Session(app)

oauth = OAuth(app)
oauth.register(
    name='github',
    client_id=os.getenv('GITHUB_CLIENT_ID'),
    client_secret=os.getenv('GITHUB_CLIENT_SECRET'),
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(320), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    avatar = db.Column(db.String(500), nullable=True)
    github_id = db.Column(db.String(9), unique=True, nullable=True)
    discord_id = db.Column(db.String(18), unique=True, nullable=True)
    books = db.relationship('BookCollection', backref='owner', lazy=True)
    wishlist = db.relationship('WishList', backref='owner', lazy=True)

    __table_args__ = (
        Index('ix_username_lower', func.lower(username), unique=True),
        Index('ix_email_lower', func.lower(email), unique=True),
    )

class BookCollection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    cover = db.Column(db.String(500), nullable=False)
    genres = db.Column(db.String(100), nullable=False)
    publisher = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    pages = db.Column(db.Integer, CheckConstraint('pages > 0 AND pages <= 9999'), nullable=False)
    isbn = db.Column(db.String(13), nullable=False)
    desc = db.Column(db.String(5000), nullable=False)
    rate = db.Column(db.Float, nullable=True)
    review = db.Column(db.String(100), nullable=True)

    def to_dict(self):
        new_date = self.date.strftime("%d-%m-%Y")

        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'cover': self.cover,
            'genres': self.genres,
            'date': new_date,
            'pages': self.pages,
            'rate': self.rate
        }
    
    def full_to_dict(self):
        new_date = self.date.strftime("%d-%m-%Y")

        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'cover': self.cover,
            'genres': self.genres,
            'publisher': self.publisher,
            'date': new_date,
            'pages': self.pages,
            'isbn': self.isbn,
            'rate': self.rate,
            'review': self.review,
            'desc': self.desc
        }

class WishList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    cover = db.Column(db.String(100), nullable=False)
    genres = db.Column(db.String(100), nullable=False)
    publisher = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    pages = db.Column(db.Integer, CheckConstraint('pages > 0 AND pages <= 9999'), nullable=False)
    isbn = db.Column(db.String(13), nullable=False)
    desc = db.Column(db.String(5000), nullable=False)
    rate = db.Column(db.Float, nullable=True)
    review = db.Column(db.String(100), nullable=True)

    def to_dict(self):
        new_date = self.date.strftime("%d-%m-%Y")

        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'cover': self.cover,
            'genres': self.genres,
            'date': new_date,
            'pages': self.pages,
            'rate': self.rate
        }
    
    def full_to_dict(self):
        new_date = self.date.strftime("%d-%m-%Y")

        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'cover': self.cover,
            'genres': self.genres,
            'publisher': self.publisher,
            'date': new_date,
            'pages': self.pages,
            'isbn': self.isbn,
            'rate': self.rate,
            'review': self.review,
            'desc': self.desc
        }

class TokenBlacklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)

with app.app_context():
    db.create_all()

def clean_expired_tokens():
    now = datetime.now(timezone.utc)
    expired = TokenBlacklist.query.filter(TokenBlacklist.expires_at < now).all()
    for jti in expired:
        db.session.delete(jti)
    db.session.commit()
    print(f"Usunięto {len(expired)} wygasłych tokenów z blacklisty.")

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token = TokenBlacklist.query.filter_by(jti=jti).first()
    return token is not None

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({"message": "Access token unieważniony."}), 401

@app.before_request
def method_override_disabler():
    if 'X-HTTP-Method-Override' in request.headers:
        return jsonify({"message": "Nagłówek X-HTTP-Method-Override jest niedozwolony."}), 403

@app.route('/api/delete-account/<string:username>', methods=['DELETE'])
@jwt_required()
def delete_account(username):
    try:
        current_user_id = get_jwt_identity()
        admin_username = os.getenv('ADMIN_USERNAME')
        user = User.query.filter(func.lower(User.username) == username.lower()).first()

        if not user:
            return jsonify({"message": "Użytkownik nie istnieje."}), 404

        if user.id != int(current_user_id) and username.lower() != admin_username.lower():
            return jsonify({"message": "Nie masz uprawnień do usunięcia tego konta."}), 403

        BookCollection.query.filter_by(user_id=user.id).delete()
        WishList.query.filter_by(user_id=user.id).delete()

        db.session.delete(user)
        db.session.commit()

        return jsonify({"message": f"Konto użytkownika '{username}' zostało pomyślnie usunięte."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Błąd podczas usuwania konta użytkownika: {str(e)}"}), 500

@app.route('/api/user/<string:username>', methods=['GET'])
@jwt_required()
def get_user(username):
    try:
        user = User.query.filter(func.lower(User.username) == username.lower()).first()

        if not user:
            return jsonify({"message": "Użytkownik nie istnieje."}), 404

        avatar_url = user.avatar if user.avatar else ""

        return jsonify({
            "username": user.username,
            "email": user.email,
            "avatar_url": avatar_url
        }), 200
    except Exception as e:
        return jsonify({"message": f"Błąd podczas pobierania danych użytkownika: {str(e)}"}), 500

@app.route('/api/users', methods=['GET'])
@jwt_required()
def get_users():
    try:
        users = User.query.all()
        user_list = []

        for user in users:
            user_list.append({
                "username": user.username,
                "email": user.email,
                "avatar_url": user.avatar if user.avatar else ""
            })

        return jsonify(user_list), 200
    except Exception as e:
        return jsonify({"message": f"Błąd podczas pobierania danych użytkowników: {str(e)}"}), 500

@app.route('/api/<string:username>/<string:type>', methods=['GET'])
@jwt_required()
def get_list(username, type):
    user = User.query.filter(func.lower(User.username) == username.lower()).first()
    if not user:
        return jsonify({"message": "Użytkownik nie istnieje."}), 404

    if type == 'bc':
        book_collection = BookCollection.query.filter_by(user_id=user.id).all()
        book_collection_data = [book.to_dict() for book in book_collection]
        return jsonify(book_collection_data), 200
    elif type == 'wl':
        wish_list = WishList.query.filter_by(user_id=user.id).all()
        wish_list_data = [book.to_dict() for book in wish_list]
        return jsonify(wish_list_data), 200

@app.route('/api/add-book/<string:type>', methods=['POST'])
@jwt_required()
def add_book(type):
    try:
        required = ['title', 'author', 'cover', 'genres', 'publisher', 'date', 'pages', 'isbn', 'desc']
        check = ['title', 'author', 'genres', 'publisher']
        data = request.get_json()
        user_id = get_jwt_identity()

        try:
            for field in required:
                if 'rate' in data and data['rate'] == '':
                    data['rate'] = None
                if 'review' in data and data['review'] == '':
                    data['review'] = None
                if field not in data:
                    return jsonify({"error": f"Brak wymaganego pola: {field}"}), 400
                if field == 'cover' and data[field] == '' or data[field] is None:
                    data[field] = 'unknown.jpg'
                if field in data and data[field] == '':
                    return jsonify({"error": f"Pole {field} nie może być puste."}), 400
                if field in check and len(data[field]) > 100:
                    return jsonify({"error": f"Pole {field} nie może mieć więcej niż 100 znaków."}), 400
                if field == 'cover' and len(data[field]) > 500 and not isinstance(data[field], (str)):
                    return jsonify({"error": "Pole cover nie może mieć więcej niż 500 znaków i musi być typu string."}), 400
                if field in check and not isinstance(data[field], (str)):
                    return jsonify({"error": f"Pole {field} musi być typu string."}), 400
                if field == 'isbn' and len(data[field]) != 13 and data[field].isdigit() and not isinstance(data[field], (str)):
                    return jsonify({"error": "Numer ISBN musi mieć 13 znaków i być typu string."}), 400
                if field == 'pages' and (int(data[field]) < 1 or int(data[field]) > 9999) and not isinstance(data[field], (int)):
                    return jsonify({"error": "Liczba stron musi być z zakresu 1-9999 i być typu int."}), 400
                if field == 'rate' and data[field] == '':
                    data[field] = None
                if field == 'review' and data[field] == '':
                    data[field] = None
                if field == 'rate' and (data[field] < 0 or data[field] > 10) and not isinstance(data[field], (int, float)):
                    return jsonify({"error": "Ocena musi być z zakresu 0-10 i być typu int lub float."}), 400
                if field == 'date' and not isinstance(data[field], (str)):
                    return jsonify({"error": "Data musi być typu string w formacie 'YYYY-MM-DD'."}), 400
                if field == 'date' and isinstance(data[field], (str)):
                    data[field] = datetime.strptime(data.get('date'), "%Y-%m-%d").date()
                if field == "desc" and len(data[field]) > 5000 and not isinstance(data[field], (str)):
                    return jsonify({"error": "Opis nie może mieć więcej niż 5000 znaków i musi być typu string."}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "Nieprawidłowy format danych."}), 400

        if type == 'bc':
            existing_book = BookCollection.query.filter_by(isbn=request.json['isbn']).first()
            if existing_book:
                return jsonify({"error": "Książka o tym numerze ISBN już istnieje w kolekcji."}), 400
            new_book = BookCollection(user_id=user_id, **data)
            db.session.add(new_book)
            db.session.commit()
            return jsonify({"message": "Książka dodana do kolekcji."}), 201
        elif type == 'wl':
            existing_book = WishList.query.filter_by(isbn=request.json['isbn']).first()
            if existing_book:
                return jsonify({"error": "Książka o tym numerze ISBN już istnieje na liście życzeń."}), 400
            new_book = WishList(user_id=user_id, **data)
            db.session.add(new_book)
            db.session.commit()
            return jsonify({"message": "Książka dodana do listy życzeń."}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Błąd podczas dodawania książki do bazy danych."}), 500

def update_book_fields(book, data):
    fields = ['title', 'author', 'cover', 'genres', 'publisher', 
              'date', 'pages', 'isbn', 'desc']
    
    for field in fields:
        if field in data:
            setattr(book, field, data.get(field))
    
    return book

def create_admin_account():
    admin_username = os.getenv('ADMIN_USERNAME')
    admin_email = os.getenv('ADMIN_EMAIL')
    admin_password = os.getenv('ADMIN_PASSWORD')

    if not admin_username or not admin_email or not admin_password:
        print("Brak danych administratora w zmiennych środowiskowych.")
        return

    existing_admin = User.query.filter(
        (func.lower(User.username) == admin_username.lower()) |
        (func.lower(User.email) == admin_email.lower())
    ).first()

    if existing_admin:
        print("Konto administratora już istnieje.")
        return

    hashed_password = bcrypt.generate_password_hash(admin_password).decode('utf-8')
    admin_user = User(username=admin_username, email=admin_email, password=hashed_password)

    try:
        db.session.add(admin_user)
        db.session.commit()
        print(f"Konto administratora '{admin_username}' zostało utworzone.")
    except Exception as e:
        db.session.rollback()
        print(f"Błąd podczas tworzenia konta administratora: {str(e)}")

@app.route('/api/edit-book/<string:type>/<int:book_id>', methods=['PATCH'])
@jwt_required()
def edit_book(type, book_id):
    try:
        data = request.get_json()
        user_id = get_jwt_identity()  

        required = ['title', 'author', 'cover', 'genres', 'publisher', 'date', 'pages', 'isbn', 'desc']
        check = ['title', 'author', 'genres', 'publisher']
        data = request.get_json()
        user_id = get_jwt_identity()

        try:
            for field in required:
                if 'rate' in data and data['rate'] == '':
                    data['rate'] = None
                if 'review' in data and data['review'] == '':
                    data['review'] = None
                if field not in data:
                    return jsonify({"error": f"Brak wymaganego pola: {field}"}), 400
                if field == 'cover' and data[field] == '' or data[field] is None:
                    data[field] = 'unknown.jpg'
                if field in data and data[field] == '':
                    return jsonify({"error": f"Pole {field} nie może być puste."}), 400
                if field in check and len(data[field]) > 100:
                    return jsonify({"error": f"Pole {field} nie może mieć więcej niż 100 znaków."}), 400
                if field == 'cover' and len(data[field]) > 500 and not isinstance(data[field], (str)):
                    return jsonify({"error": "Pole cover nie może mieć więcej niż 500 znaków i musi być typu string."}), 400
                if field in check and not isinstance(data[field], (str)):
                    return jsonify({"error": f"Pole {field} musi być typu string."}), 400
                if field == 'isbn' and len(data[field]) != 13 and data[field].isdigit() and not isinstance(data[field], (str)):
                    return jsonify({"error": "Numer ISBN musi mieć 13 znaków i być typu string."}), 400
                if field == 'pages' and (int(data[field]) < 1 or int(data[field]) > 9999) and not isinstance(data[field], (int)):
                    return jsonify({"error": "Liczba stron musi być z zakresu 1-9999 i być typu int."}), 400
                if field == 'rate' and data[field] == '':
                    data[field] = None
                if field == 'review' and data[field] == '':
                    data[field] = None
                if field == 'rate' and (data[field] < 0 or data[field] > 10) and not isinstance(data[field], (int, float)):
                    return jsonify({"error": "Ocena musi być z zakresu 0-10 i być typu int lub float."}), 400
                if field == 'date' and not isinstance(data[field], (str)):
                    return jsonify({"error": "Data musi być typu string w formacie 'YYYY-MM-DD'."}), 400
                if field == 'date' and isinstance(data[field], (str)):
                    data[field] = datetime.strptime(data.get('date'), "%Y-%m-%d").date()
                if field == "desc" and len(data[field]) > 5000 and not isinstance(data[field], (str)):
                    return jsonify({"error": "Opis nie może mieć więcej niż 5000 znaków i musi być typu string."}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "Nieprawidłowy format danych."}), 400

        if type == 'bc':
            book = BookCollection.query.filter_by(id=book_id, user_id=user_id).first()
            if not book:
                return jsonify({"message": "Brak książki w kolekcji."}), 404
            book = update_book_fields(book, data)
            db.session.commit()
            return jsonify({"message": "Książka z kolekcji zaktualizowana."}), 200
        elif type == 'wl':
            book = WishList.query.filter_by(id=book_id, user_id=user_id).first()
            if not book:
                return jsonify({"message": "Brak książki na liście życzeń."}), 404
            book = update_book_fields(book, data)
            db.session.commit()
            return jsonify({"message": "Książka z listy życzeń zaktualizowana."}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Błąd podczas aktualizowania książki w bazie danych."}), 500

@app.route('/api/review-book/<string:type>/<int:book_id>', methods=['PATCH'])
@jwt_required()
def review_book(type, book_id):
    try:
        user_id = get_jwt_identity()   
        data = request.get_json()

        try:
            if 'rate' not in data:
                return jsonify({"error": "Brak wymaganego pola: rate"}), 400
            if 'review' not in data:
                return jsonify({"error": "Brak wymaganego pola: review"}), 400
            if data['rate'] == '':
                data['rate'] = None
            if data['review'] == '':
                data['review'] = None
            if data['rate'] is not None and isinstance(data['rate'], float) and (float(data["rate"]) < 0 or float(data["rate"]) > 10):
                return jsonify({"error": "Ocena musi być z zakresu 0-10 i być typu float."}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "Nieprawidłowy format danych."}), 400

        if type == 'bc':
            book = BookCollection.query.filter_by(id=book_id, user_id=user_id).first()
            if not book:
                return jsonify({"message": "Brak książki w kolekcji."}), 404
            book.rate = data.get("rate")
            book.review = data.get("review")
            db.session.commit()
            return jsonify({"message": "Recenzja książki z kolekcji zaktualizowana."}), 200
        elif type == 'wl':
            book = WishList.query.filter_by(id=book_id, user_id=user_id).first()
            if not book:
                return jsonify({"message": "Brak książki na liście życzeń."}), 404
            book.rate = data.get("rate")
            book.review = data.get("review")
            db.session.commit()
            return jsonify({"message": "Recenzja książki z listy życzeń zaktualizowana."}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Błąd podczas aktualizowania recenzji książki w bazie danych."}), 500

@app.route('/api/book-details/<string:type>/<int:book_id>', methods=['GET'])
@jwt_required()
def get_book(type, book_id):
    try:
        user_id = get_jwt_identity()
        if type == 'bc':
            book = BookCollection.query.filter_by(id=book_id, user_id=user_id).first()
            if not book:
                return jsonify({"message": "Brak ksiązki w kolekcji."}), 404
            book_data = book.full_to_dict()
            return jsonify(book_data), 200
        elif type == 'wl':
            book = WishList.query.filter_by(id=book_id, user_id=user_id).first()
            if not book:
                return jsonify({"message": "Brak książki na liście życzeń."}), 404
            book_data = book.full_to_dict()
            return jsonify(book_data), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Błąd podczas pobierania książki z bazy danych."}), 500

@app.route('/api/book-exists/<string:type>/<int:book_id>', methods=['GET'])
@jwt_required()
def check_book_exists(type, book_id):
    try:
        user_id = get_jwt_identity()
        if type == 'bc':
            book_exists = BookCollection.query.filter_by(id=book_id, user_id=user_id).first() is not None
            return jsonify({"exists": book_exists}), 200
        elif type == 'wl':
            book_exists = WishList.query.filter_by(id=book_id, user_id=user_id).first() is not None
            return jsonify({"exists": book_exists}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Błąd podczas sprawdzania książki w bazie danych."}), 500

@app.route('/api/remove-all-books/<string:type>', methods=['DELETE'])
@jwt_required()
def remove_all_books(type):
    try:
        user_id = get_jwt_identity()

        if type == 'bc':
            books = BookCollection.query.filter_by(user_id=user_id).all()
            if not books:
                return jsonify({"message": "Brak książek na liście życzeń."}), 404
            count = len(books)
            for book in books:
                db.session.delete(book)
            db.session.commit()
            return jsonify({"message": f"Usunięto wszystkie książki ({count}) z kolekcji."}), 200
        elif type == 'wl':
            books = WishList.query.filter_by(user_id=user_id).all()
            if not books:
                return jsonify({"message": "Brak książek w kolekcji."}), 404
            count = len(books)
            for book in books:
                db.session.delete(book)
            db.session.commit()
            return jsonify({"message": f"Usunięto wszystkie książki ({count}) z listy życzeń."}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Błąd podczas usuwania książek z bazy danych."}), 500

@app.route('/api/remove-book/<string:type>/<int:book_id>', methods=['DELETE'])
@jwt_required()
def bc_remove_book(type, book_id):
    try:
        user_id = get_jwt_identity()

        if type == 'bc':
            book = BookCollection.query.filter_by(id=book_id, user_id=user_id).first()
            if not book:
                return jsonify({"message": "Brak książki w kolekcji."}), 404
            db.session.delete(book)
            remaining_books = BookCollection.query.filter_by(user_id=user_id).order_by(BookCollection.id).all()
            for idx, remaining_book in enumerate(remaining_books, start=1):
                remaining_book.id = idx
            db.session.commit()
            return jsonify({"message": "Książka usunięta z kolekcji."}), 200
        elif type == 'wl':
            book = WishList.query.filter_by(id=book_id, user_id=user_id).first()
            if not book:
                return jsonify({"message": "Brak książki na liście życzeń."}), 404
            db.session.delete(book)
            remaining_books = WishList.query.filter_by(user_id=user_id).order_by(WishList.id).all()
            for idx, remaining_book in enumerate(remaining_books, start=1):
                remaining_book.id = idx
            db.session.commit()
            return jsonify({"message": "Książka usunięta z listy życzeń."}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Błąd podczas usuwania książki z bazy danych."}), 500

@app.route('/api/move-book-to/<string:type>//<int:book_id>', methods=['POST'])
@jwt_required()
def move_book_to(type, book_id):
    try:
        user_id = get_jwt_identity()

        if type == 'bc':
            book = BookCollection.query.filter_by(id=book_id, user_id=user_id).first()
            if not book:
                return jsonify({"message": "Brak książki w kolekcji."}), 404
            new_book = WishList(**{col: getattr(book, col) for col in book.__table__.columns.keys() if col != 'id'})
            new_book.user_id = user_id
            db.session.add(new_book)
            db.session.delete(book)
            remaining_books = BookCollection.query.filter_by(user_id=user_id).order_by(BookCollection.id).all()
            for idx, remaining_book in enumerate(remaining_books, start=1):
                remaining_book.id = idx
            db.session.commit()
            return jsonify({"message": "Książka przeniesiona na listę życzeń."}), 200
        elif type == 'wl':
            book = WishList.query.filter_by(id=book_id, user_id=user_id).first()
            if not book:
                return jsonify({"message": "Brak książki na liście życzeń."}), 404
            new_book = BookCollection(**{col: getattr(book, col) for col in book.__table__.columns.keys() if col != 'id'})
            new_book.user_id = user_id
            db.session.add(new_book)
            db.session.delete(book)
            remaining_books = WishList.query.filter_by(user_id=user_id).order_by(WishList.id).all()
            for idx, remaining_book in enumerate(remaining_books, start=1):
                remaining_book.id = idx
            db.session.commit()
            return jsonify({"message": "Książka przeniesiona do kolekcji."}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Błąd podczas przenoszenia książki."}), 500

@app.route('/api/refresh', methods=['POST'])
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
        refresh_expires_delta = timedelta(days=1)

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

@app.route('/api/logout', methods=['POST'])
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
            jti=jti,
            expires_at=access_expiration
        )

        refresh_expiration = datetime.fromtimestamp(decoded_token['exp'])
        refresh_blacklist = TokenBlacklist(
            jti=refresh_jti,
            expires_at=refresh_expiration
        )

        db.session.add(access_blacklist)
        db.session.add(refresh_blacklist)
        db.session.commit()

        return jsonify({"message": "Wylogowano pomyślnie."}), 200
    except Exception as e:
        return jsonify({"message": "Błąd podczas wylogowania: " + str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('usernameOrEmail')).first() or User.query.filter_by(username=data.get('usernameOrEmail')).first()
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
            refresh_expires_delta = timedelta(days=31)
        else:
            refresh_token_expire = "00:01:00:00"
            refresh_expires_delta = timedelta(days=1)

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

@app.route('/api/register', methods=['POST'])
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
        refresh_expires_delta = timedelta(days=1)

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

@app.route('/api/clear-session', methods=['GET'])
def clear_session():
    response = make_response(jsonify({"message": "Ciasteczko 'session' usunięte."}))
    response.delete_cookie("session")
    return response, 200

@app.route('/api/login/discord')
def login_discord():
    return discord.create_session(scope=["identify", "email"])

@app.route('/api/login/github')
def login_github():
    redirect_uri = url_for('auth_github', _external=True)
    return oauth.github.authorize_redirect(redirect_uri)

@app.route('/api/auth/discord')
def auth_discord():
    try:
        error = request.args.get("error")
        if error == "access_denied":
            response = redirect("http://localhost:5173/login")
            response.delete_cookie("session")
            return response
        
        token = discord.callback()
        discord_user = discord.fetch_user()

        discord_id = str(discord_user.id)
        username = discord_user.name
        email = discord_user.email
        avatar_url = discord_user.avatar_url
        
        if not email:
            return jsonify({"message": "Nie udało się pobrać adresu email z Discord."}), 400
        
        user = User.query.filter((User.discord_id == discord_id) | (func.lower(User.username) == username.lower()) | (func.lower(User.email) == email.lower())).first()

        if user:
            if not user.discord_id:
                user.discord_id = discord_id
            if not user.avatar and avatar_url:
                user.avatar = avatar_url
            db.session.commit()
        else:
            if User.query.filter_by(username=username).first():
                username = f"{username}_{random.randint(1000,9999)}"
                
            random_password = bcrypt.generate_password_hash(os.urandom(16)).decode('utf-8')
            user = User(
                username=username, 
                email=email, 
                password=random_password, 
                avatar=avatar_url,
                discord_id=discord_id
            )
            db.session.add(user)
            db.session.commit()
        
        access_expires_delta = timedelta(minutes=10)
        refresh_expires_delta = timedelta(days=1)

        access_token = create_access_token(identity=str(user.id), expires_delta=access_expires_delta)
        refresh_token = create_refresh_token(identity=str(user.id), expires_delta=refresh_expires_delta)

        access_token_expire_date = datetime.now(timezone.utc) + access_expires_delta
        refresh_token_expire_date = datetime.now(timezone.utc) + refresh_expires_delta
        
        response = redirect("http://localhost:5173/home") 
        response.set_cookie("access_token", access_token, expires=access_token_expire_date, httponly=False, samesite='Lax', secure=True)
        response.set_cookie("refresh_token", refresh_token, expires=refresh_token_expire_date, httponly=False, samesite='Lax', secure=True)
        response.set_cookie("username", str(user.username), expires=access_token_expire_date, httponly=False, samesite='Lax', secure=True)

        return response
        
    except Exception as e:
        return jsonify({"message": f"Błąd podczas autentykacji Discord: {str(e)}"}), 500

@app.route('/api/auth/github')
def auth_github():
    error = request.args.get("error")
    if error == "access_denied":
        response = redirect("/login")
        response.delete_cookie("session")
        
        return response

    token = oauth.github.authorize_access_token()
    user_data = oauth.github.get('user').json()
    github_id = str(user_data.get("id"))
    email = user_data.get("email")
    username = user_data.get("login")
    avatar_url = user_data.get("avatar_url")
    
    if not email:
        emails = oauth.github.get('user/emails').json()
        for em in emails:
            if em.get("primary") and em.get("verified"):
                email = em.get("email")
                break
    if not email:
        return jsonify({"message": "Nie udało się pobrać adresu email z GitHub."}), 400

    link_account = request.args.get("link", "false").lower() == "true"
    if link_account:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"message": "Brak tokenu JWT do powiązania konta."}), 401
        try:
            token_str = auth_header.split(" ")[1]
            decoded = decode_token(token_str)
            current_user_id = decoded['sub']
        except Exception as e:
            return jsonify({"message": "Nieprawidłowy token JWT."}), 401

        current_user = User.query.get(current_user_id)
        if current_user is None:
            return jsonify({"message": "Nie znaleziono użytkownika."}), 404

        if current_user.github_id and current_user.github_id != github_id:
            return jsonify({"message": "Twoje konto jest już powiązane z innym GitHub."}), 400

        current_user.github_id = github_id
        if not current_user.avatar and avatar_url:
            current_user.avatar = avatar_url
        db.session.commit()
        return jsonify({"message": "Konto GitHub zostało pomyślnie powiązane."}), 200

    user = User.query.filter((User.github_id == github_id) | (func.lower(User.username) == username.lower()) | (func.lower(User.email) == email.lower())).first()

    if user:
        if not user.github_id:
            user.github_id = github_id
        if not user.avatar and avatar_url:
            user.avatar = avatar_url
        db.session.commit()

        access_expires_delta = timedelta(minutes=10)
        refresh_expires_delta = timedelta(days=1)
        access_token = create_access_token(identity=str(user.id), expires_delta=access_expires_delta)
        refresh_token = create_refresh_token(identity=str(user.id), expires_delta=refresh_expires_delta)

        access_token_expire_date = datetime.now(timezone.utc) + access_expires_delta
        refresh_token_expire_date = datetime.now(timezone.utc) + refresh_expires_delta
        
        response = redirect("http://localhost:5173/home") 
        response.set_cookie("access_token", access_token, expires=access_token_expire_date, httponly=False, samesite='Lax', secure=True)
        response.set_cookie("refresh_token", refresh_token, expires=refresh_token_expire_date, httponly=False, samesite='Lax', secure=True)
        response.set_cookie("username", str(user.username), expires=access_token_expire_date, httponly=False, samesite='Lax', secure=True)

        return response
    else:
        username = user_data.get("login")
        if User.query.filter_by(username=username).first():
            username = f"{username}_{random.randint(1000,9999)}"
        random_password = bcrypt.generate_password_hash(os.urandom(16)).decode('utf-8')
        new_user = User(username=username, email=email, password=random_password, avatar=avatar_url, github_id=github_id)
        db.session.add(new_user)
        db.session.commit()

        access_expires_delta = timedelta(minutes=10)
        refresh_expires_delta = timedelta(days=1)
        access_token = create_access_token(identity=str(new_user.id), expires_delta=access_expires_delta)
        refresh_token = create_refresh_token(identity=str(new_user.id), expires_delta=refresh_expires_delta)

        access_token_expire_date = datetime.now(timezone.utc) + access_expires_delta
        refresh_token_expire_date = datetime.now(timezone.utc) + refresh_expires_delta

        response = redirect("http://localhost:5173/home") 
        response.set_cookie("access_token", access_token, expires=access_token_expire_date, httponly=False, samesite='Lax', secure=True)
        response.set_cookie("refresh_token", refresh_token, expires=refresh_token_expire_date, httponly=False, samesite='Lax', secure=True)
        response.set_cookie("username", str(new_user.username), expires=access_token_expire_date, httponly=False, samesite='Lax', secure=True)

        return response

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"message": "Endpoint nie istnieje."}), 404

if __name__ == '__main__':
    with app.app_context():
        create_admin_account()
        clean_expired_tokens()
    app.run(port=app.config['SERVER_PORT'], debug=True)