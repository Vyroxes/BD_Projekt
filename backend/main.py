from flask import Flask, request, jsonify, make_response, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from flask_jwt_extended.utils import decode_token
from flask_cors import CORS
from datetime import timedelta, datetime, timezone
from sqlalchemy.exc import IntegrityError
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
import random
import os

load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True)

app.config['SERVER_PORT'] = os.getenv('SERVER_PORT')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_ACCESS_TOKEN_SECRET'] = os.getenv('JWT_ACCESS_TOKEN_SECRET')
app.config['JWT_REFRESH_TOKEN_SECRET'] = os.getenv('JWT_REFRESH_TOKEN_SECRET')
app.config['JWT_ACCESS_TOKEN_EXPIRE'] = timedelta(minutes=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRE')))
app.config['JWT_ACCESS_TOKEN_REMEMBER_EXPIRE'] = timedelta(minutes=int(os.getenv('JWT_ACCESS_TOKEN_REMEMBER_EXPIRE')))
app.config['JWT_REFRESH_TOKEN_EXPIRE'] = timedelta(hours=int(os.getenv('JWT_REFRESH_TOKEN_EXPIRE')))
app.config['JWT_REFRESH_TOKEN_REMEMBER_EXPIRE'] = timedelta(days=int(os.getenv('JWT_REFRESH_TOKEN_REMEMBER_EXPIRE')))
app.secret_key = os.getenv('FLASK_SECRET_KEY')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

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
    password = db.Column(db.String(255), nullable=False)
    github_id = db.Column(db.String(255), unique=True, nullable=True)
    books = db.relationship('BookCollection', backref='owner', lazy=True)
    wishlist = db.relationship('WishList', backref='owner', lazy=True)

class BookCollection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    cover = db.Column(db.String(100), nullable=False)
    genres = db.Column(db.String(100), nullable=False)
    publisher = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    pages = db.Column(db.Integer, nullable=False)
    isbn = db.Column(db.String(20), nullable=False)
    rate = db.Column(db.Float, nullable=True)
    review = db.Column(db.String(100), nullable=True)
    desc = db.Column(db.String(1000), nullable=False)

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
    pages = db.Column(db.Integer, nullable=False)
    isbn = db.Column(db.String(20), nullable=False)
    rate = db.Column(db.Float, nullable=True)
    review = db.Column(db.String(100), nullable=True)
    desc = db.Column(db.String(1000), nullable=False)

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
    for token in expired:
        db.session.delete(token)
    db.session.commit()
    print(f"Usunięto {len(expired)} wygasłych tokenów z blacklisty.")

@app.before_request
def initialize():
    if random.random() < 0.2:
        clean_expired_tokens()

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token = TokenBlacklist.query.filter_by(jti=jti).first()
    return token is not None

@app.route('/api/book-collection', methods=['GET'])
@jwt_required()
def get_books():
    user_id = get_jwt_identity()
    book_collection = BookCollection.query.filter_by(user_id=user_id).all()

    book_collection_data = [book.to_dict() for book in book_collection]

    return jsonify(book_collection_data), 200

@app.route('/api/wish-list', methods=['GET'])
@jwt_required()
def get_wishlist():
    user_id = get_jwt_identity()
    wish_list = WishList.query.filter_by(user_id=user_id).all()

    wish_list_data = [book.to_dict() for book in wish_list]

    return jsonify(wish_list_data), 200


@app.route('/api/bc-add-book', methods=['POST'])
@jwt_required()
def bc_add_book():
    try:
        existing_book = BookCollection.query.filter_by(isbn=request.json['isbn']).first()
        if existing_book:
            return jsonify({"error": "Książka o tym numerze ISBN już istnieje w kolekcji."}), 400

        user_id = get_jwt_identity()
        data = request.get_json()
        date_value = data.get('date')

        if isinstance(date_value, str):
            date = datetime.strptime(date_value, "%Y-%m-%d").date()
        elif isinstance(date_value, datetime):
            date = date_value.date()
        elif isinstance(date_value, date):
            date = date_value
        else:
            return jsonify({"error": "Nieprawidłowy format daty."}), 400

        new_book = BookCollection(user_id=user_id, **data)
        new_book.date = date
        db.session.add(new_book)
        db.session.commit()
        return jsonify({"message": "Książka dodana do kolekcji."}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Błąd podczas dodawania książki do bazy danych."}), 500
    
@app.route('/api/wl-add-book', methods=['POST'])
@jwt_required()
def wl_add_book():
    try:
        existing_book = WishList.query.filter_by(isbn=request.json['isbn']).first()
        if existing_book:
            return jsonify({"error": "Książka o tym numerze ISBN już istnieje na liście życzeń."}), 400

        user_id = get_jwt_identity()
        data = request.get_json()
        date_value = data.get('date')

        if isinstance(date_value, str):
            date = datetime.strptime(date_value, "%Y-%m-%d").date()
        elif isinstance(date_value, datetime):
            date = date_value.date()
        elif isinstance(date_value, date):
            date = date_value
        else:
            return jsonify({"error": "Nieprawidłowy format daty."}), 400

        new_book = WishList(user_id=user_id, **data)
        new_book.date = date
        db.session.add(new_book)
        db.session.commit()
        return jsonify({"message": "Książka dodana do listy życzeń."}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Błąd podczas dodawania książki do bazy danych."}), 500

@app.route('/api/bc-edit-book/<int:book_id>', methods=['POST'])
@jwt_required()
def bc_edit_book(book_id):
    user_id = get_jwt_identity()
    book = BookCollection.query.filter_by(id=book_id, user_id=user_id).first()
    if not book:
        return jsonify({"message": "Brak książki w kolekcji."}), 404
    
    data = request.get_json()
    date_value = data.get('date')

    if isinstance(date_value, str):
        date = datetime.strptime(date_value, "%Y-%m-%d").date()
    elif isinstance(date_value, datetime):
        date = date_value.date()
    elif isinstance(date_value, date):
        date = date_value
    else:
        return jsonify({"error": "Nieprawidłowy format daty."}), 400

    book.title = data.get("title", book.title)
    book.author = data.get("author", book.author)
    book.cover = data.get("cover", book.cover)
    book.genres = data.get("genres", book.genres)
    book.publisher = data.get("publisher", book.publisher)
    book.date = date
    book.pages = data.get("pages", book.pages)
    book.isbn = data.get("isbn", book.isbn)
    book.desc = data.get("desc", book.desc)

    db.session.commit()
    return jsonify({"message": "Książka z kolekcji zaktualizowana."}), 200

@app.route('/api/wl-edit-book/<int:book_id>', methods=['POST'])
@jwt_required()
def wl_edit_book(book_id):
    user_id = get_jwt_identity()
    book = WishList.query.filter_by(id=book_id, user_id=user_id).first()
    if not book:
        return jsonify({"message": "Brak książki na liście życzeń."}), 404

    data = request.get_json()
    date_value = data.get('date')

    if isinstance(date_value, str):
        date = datetime.strptime(date_value, "%Y-%m-%d").date()
    elif isinstance(date_value, datetime):
        date = date_value.date()
    elif isinstance(date_value, date):
        date = date_value
    else:
        return jsonify({"error": "Nieprawidłowy format daty."}), 400

    book.title = data.get("title", book.title)
    book.author = data.get("author", book.author)
    book.cover = data.get("cover", book.cover)
    book.genres = data.get("genres", book.genres)
    book.publisher = data.get("publisher", book.publisher)
    book.date = date
    book.pages = data.get("pages", book.pages)
    book.isbn = data.get("isbn", book.isbn)
    book.desc = data.get("desc", book.desc)

    db.session.commit()
    return jsonify({"message": "Książka z listy życzeń zaktualizowana."}), 200

@app.route('/api/bc-review-book/<int:book_id>', methods=['POST'])
@jwt_required()
def bc_review_book(book_id):
    user_id = get_jwt_identity()
    book = BookCollection.query.filter_by(id=book_id, user_id=user_id).first()
    if not book:
        return jsonify({"message": "Brak książki w kolekcji."}), 404
    
    data = request.get_json()

    book.rate = data.get("rate") if data.get("rate") != "" else None
    book.review = data.get("review") if data.get("review") != "" else None

    db.session.commit()
    return jsonify({"message": "Książka z kolekcji zaktualizowana."}), 200

@app.route('/api/wl-review-book/<int:book_id>', methods=['POST'])
@jwt_required()
def wl_review_book(book_id):
    user_id = get_jwt_identity()
    book = WishList.query.filter_by(id=book_id, user_id=user_id).first()
    if not book:
        return jsonify({"message": "Brak książki na liście życzeń."}), 404

    data = request.get_json()

    book.rate = data.get("rate", book.rate)
    book.review = data.get("review", book.review)

    db.session.commit()
    return jsonify({"message": "Książka z listy życzeń zaktualizowana."}), 200

@app.route('/api/bc-book-details/<int:book_id>', methods=['GET'])
@jwt_required()
def bc_get_book(book_id):
    user_id = get_jwt_identity()
    book = BookCollection.query.filter_by(id=book_id, user_id=user_id).first()
    if not book:
        return jsonify({"message": "Brak ksiązki w kolekcji."}), 404

    book_data = book.full_to_dict()

    return jsonify(book_data), 200

@app.route('/api/wl-book-details/<int:book_id>', methods=['GET'])
@jwt_required()
def wl_get_book(book_id):
    user_id = get_jwt_identity()
    book = WishList.query.filter_by(id=book_id, user_id=user_id).first()
    if not book:
        return jsonify({"message": "Brak książki na liście życzeń."}), 404

    book_data = book.full_to_dict()

    return jsonify(book_data), 200

@app.route('/api/bc-book-exists/<int:book_id>', methods=['GET'])
@jwt_required()
def bc_check_book_exists(book_id):
    user_id = get_jwt_identity()
    book_exists = BookCollection.query.filter_by(id=book_id, user_id=user_id).first() is not None

    return jsonify({"exists": book_exists}), 200

@app.route('/api/wl-book-exists/<int:book_id>', methods=['GET'])
@jwt_required()
def wl_check_book_exists(book_id):
    user_id = get_jwt_identity()
    book_exists = WishList.query.filter_by(id=book_id, user_id=user_id).first() is not None

    return jsonify({"exists": book_exists}), 200


@app.route('/api/bc-remove-all-books', methods=['DELETE'])
@jwt_required()
def bc_remove_all_books():
    user_id = get_jwt_identity()
    books = BookCollection.query.filter_by(user_id=user_id).all()
    
    if not books:
        return jsonify({"message": "Brak książek w kolekcji."}), 404
    
    count = len(books)
    for book in books:
        db.session.delete(book)
    
    db.session.commit()
    return jsonify({"message": f"Usunięto wszystkie książki ({count}) z kolekcji."}), 200

@app.route('/api/wl-remove-all-books', methods=['DELETE'])
@jwt_required()
def wl_remove_all_books():
    user_id = get_jwt_identity()
    books = WishList.query.filter_by(user_id=user_id).all()
    
    if not books:
        return jsonify({"message": "Brak książek na liście życzeń."}), 404
    
    count = len(books)
    for book in books:
        db.session.delete(book)
    
    db.session.commit()
    return jsonify({"message": f"Usunięto wszystkie książki ({count}) z listy życzeń."}), 200

@app.route('/api/bc-remove-book/<int:book_id>', methods=['DELETE'])
@jwt_required()
def bc_remove_book(book_id):
    user_id = get_jwt_identity()
    book = BookCollection.query.filter_by(id=book_id, user_id=user_id).first()
    if not book:
        return jsonify({"message": "Brak książki w kolekcji."}), 404

    db.session.delete(book)

    remaining_books = BookCollection.query.filter_by(user_id=user_id).order_by(BookCollection.id).all()
    for idx, remaining_book in enumerate(remaining_books, start=1):
        remaining_book.id = idx

    db.session.commit()
    return jsonify({"message": "Książka usunięta."}), 200

@app.route('/api/wl-remove-book/<int:book_id>', methods=['DELETE'])
@jwt_required()
def wl_remove_book(book_id):
    user_id = get_jwt_identity()
    book = WishList.query.filter_by(id=book_id, user_id=user_id).first()
    if not book:
        return jsonify({"message": "Brak książki na liście życzeń."}), 404

    db.session.delete(book)

    remaining_books = WishList.query.filter_by(user_id=user_id).order_by(WishList.id).all()
    for idx, remaining_book in enumerate(remaining_books, start=1):
        remaining_book.id = idx

    db.session.commit()
    return jsonify({"message": "Książka usunięta."}), 200

@app.route('/api/move-book-to-wl/<int:book_id>', methods=['POST'])
@jwt_required()
def move_to_wl(book_id):
    user_id = get_jwt_identity()
    book = BookCollection.query.filter_by(id=book_id, user_id=user_id).first()
    if not book:
        return jsonify({"message": "Brak książki w kolekcji."}), 404

    new_wish = WishList(**{col: getattr(book, col) for col in book.__table__.columns.keys() if col != 'id'})
    new_wish.user_id = user_id
    db.session.add(new_wish)
    db.session.delete(book)

    remaining_books = BookCollection.query.filter_by(user_id=user_id).order_by(BookCollection.id).all()
    for idx, remaining_book in enumerate(remaining_books, start=1):
        remaining_book.id = idx

    db.session.commit()
    return jsonify({"message": "Książka przeniesiona do listy życzeń."}), 200

@app.route('/api/move-book-to-bc/<int:book_id>', methods=['POST'])
@jwt_required()
def move_to_bc(book_id):
    user_id = get_jwt_identity()
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
            return jsonify({"message": "Token unieważniony."}), 401

        access_token_expire = app.config['JWT_ACCESS_TOKEN_EXPIRE']
        refresh_token_expire = app.config['JWT_REFRESH_TOKEN_EXPIRE']

        access_token = create_access_token(identity=str(user.id), expires_delta=access_token_expire)
        refresh_token = create_refresh_token(identity=str(user.id), expires_delta=refresh_token_expire)

        return jsonify({
            "message": "Token odświeżony pomyślnie",
            "username": user.username,
            "email": user.email,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expire_time": str(access_token_expire),
            "refresh_expire_time": str(refresh_token_expire)
        }), 200

    except Exception as e:
        return jsonify({"message": "Błąd podczas odświeżania tokenu: " + str(e)}), 500

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
        refresh_user_id = decoded_token['sub']
        refresh_user = User.query.filter_by(id=refresh_user_id).first()

        if not user or not refresh_user:
            return jsonify({"message": "Użytkownik nie istnieje."}), 404
        
        if user != refresh_user:
            return jsonify({"message": "Nieprawidłowe tokeny."}), 404
        
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

    if user and bcrypt.check_password_hash(user.password, data.get('password')):
        if data.get('remember'):
            access_token_expire = app.config['JWT_ACCESS_TOKEN_REMEMBER_EXPIRE']
            refresh_token_expire = app.config['JWT_REFRESH_TOKEN_REMEMBER_EXPIRE']
        else:
            access_token_expire = app.config['JWT_ACCESS_TOKEN_EXPIRE']
            refresh_token_expire = app.config['JWT_REFRESH_TOKEN_EXPIRE']

        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

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

    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({"message": "Nazwa użytkownika jest już zajęta."}), 400
    
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({"message": "Email jest już zajęty."}), 400

    hashed_password = bcrypt.generate_password_hash(data.get('password')).decode('utf-8')

    new_user = User(username=data.get('username'), email=data.get('email'), password=hashed_password)

    try:
        db.session.add(new_user)
        db.session.commit()

        access_token_expires = app.config['JWT_ACCESS_TOKEN_EXPIRES']
        refresh_token_expires = app.config['JWT_REFRESH_TOKEN_EXPIRES']

        access_token = create_access_token(identity=str(new_user.id))
        refresh_token = create_refresh_token(identity=str(new_user.id))

        response = make_response(jsonify({
            "message": "Rejestracja pomyślna",
            "username": new_user.username,
            "email": new_user.email,
            "access_token": str(access_token),
            "refresh_token": str(refresh_token),
            "expire_time": str(access_token_expires),
            "refresh_expire_time": str(refresh_token_expires)
        }))

        return response, 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Błąd podczas rejestracji: " + str(e)}), 500

@app.route('/api/login/github')
def login_github():
    redirect_uri = url_for('auth_github', _external=True)
    return oauth.github.authorize_redirect(redirect_uri)

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
        db.session.commit()
        return jsonify({"message": "Konto GitHub zostało pomyślnie powiązane."}), 200

    user = User.query.filter((User.github_id == github_id) | (User.email == email)).first()
    if user:
        if not user.github_id:
            user.github_id = github_id
            db.session.commit()
        access_token_expires = app.config['JWT_ACCESS_TOKEN_EXPIRES']
        refresh_token_expires = app.config['JWT_REFRESH_TOKEN_EXPIRES']
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        access_token_expire_date = datetime.now(timezone.utc) + access_token_expires
        refresh_token_expire_date = datetime.now(timezone.utc) + refresh_token_expires
        
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
        new_user = User(username=username, email=email, password=random_password, github_id=github_id)
        db.session.add(new_user)
        db.session.commit()
        access_token_expires = app.config['JWT_ACCESS_TOKEN_EXPIRES']
        refresh_token_expires = app.config['JWT_REFRESH_TOKEN_EXPIRES']
        access_token = create_access_token(identity=str(new_user.id))
        refresh_token = create_refresh_token(identity=str(new_user.id))

        response = redirect("http://localhost:5173/home") 
        response.set_cookie("access_token", access_token, httponly=False, samesite='Lax', secure=True)
        response.set_cookie("refresh_token", refresh_token, httponly=False, samesite='Lax', secure=True)
        response.set_cookie("username", str(new_user.username), httponly=False, samesite='Lax', secure=True)

        return response

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"message": "Endpoint nie istnieje."}), 404

if __name__ == '__main__':
    app.run(port=app.config['SERVER_PORT'], debug=True)