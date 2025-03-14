from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from datetime import timedelta, datetime
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
CORS(app, supports_credentials=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'zA.w>5rtF?MscTJm,owF'  
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(seconds=5)
app.config['JWT_ACCESS_TOKEN_REMEMBER_EXPIRES'] = timedelta(days=7)
#app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(hours=1)
#app.config['JWT_REFRESH_TOKEN_REMEMBER_EXPIRES'] = timedelta(days=7)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(320), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
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
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'cover': self.cover
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
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'cover': self.cover
        }

with app.app_context():
    db.create_all()

@app.route('/book-collection', methods=['GET'])
@jwt_required()
def get_books():
    user_id = get_jwt_identity()
    books = BookCollection.query.filter_by(user_id=user_id).all()

    books_data = [book.to_dict() for book in books]

    return jsonify(books_data), 200

@app.route('/wish-list', methods=['GET'])
@jwt_required()
def get_wishlist():
    user_id = get_jwt_identity()
    wishlist = WishList.query.filter_by(user_id=user_id).all()
    return jsonify([book.__dict__ for book in wishlist]), 200


@app.route('/add-book', methods=['POST'])
@jwt_required()
def add_book():
    try:
        existing_book = BookCollection.query.filter_by(isbn=request.json['isbn']).first()
        if existing_book:
            return jsonify({"error": "Książka o tym numerze ISBN już istnieje w kolekcji."}), 400

        user_id = get_jwt_identity()
        data = request.get_json()

        date = datetime.strptime(data.get('date'), "%Y-%m-%d").date()

        new_book = BookCollection(user_id=user_id, **data)
        new_book.date = date
        db.session.add(new_book)
        db.session.commit()
        return jsonify({"message": "Książka dodana do kolekcji"}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Błąd podczas dodawania książki do bazy danych."}), 500

@app.route('/remove-book/<int:book_id>', methods=['DELETE'])
@jwt_required()
def remove_book(book_id):
    user_id = get_jwt_identity()
    book = BookCollection.query.filter_by(id=book_id, user_id=user_id).first()
    if not book:
        return jsonify({"message": "Nie znaleziono książki"}), 404

    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Książka usunięta"}), 200

@app.route('/move-book-to-wishlist/<int:book_id>', methods=['POST'])
@jwt_required()
def move_to_wishlist(book_id):
    user_id = get_jwt_identity()
    book = BookCollection.query.filter_by(id=book_id, user_id=user_id).first()
    if not book:
        return jsonify({"message": "Nie znaleziono książki"}), 404

    new_wish = WishList(user_id=user_id, **{col: getattr(book, col) for col in book.__table__.columns.keys() if col != 'id'})
    db.session.add(new_wish)
    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Książka przeniesiona do listy życzeń"}), 200

@app.route('/move-book-to-collection/<int:book_id>', methods=['POST'])
@jwt_required()
def move_to_collection(book_id):
    user_id = get_jwt_identity()
    book = WishList.query.filter_by(id=book_id, user_id=user_id).first()
    if not book:
        return jsonify({"message": "Nie znaleziono książki"}), 404

    new_book = BookCollection(user_id=user_id, **{col: getattr(book, col) for col in book.__table__.columns.keys() if col != 'id'})
    db.session.add(new_book)
    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Książka przeniesiona do kolekcji"}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('usernameOrEmail')).first() or User.query.filter_by(username=data.get('usernameOrEmail')).first()

    if user and bcrypt.check_password_hash(user.password, data.get('password')):
        if data.get('remember'):
            access_token_expires = app.config['JWT_ACCESS_TOKEN_REMEMBER_EXPIRES']
            #refresh_token_expires = app.config['JWT_REFRESH_TOKEN_REMEMBER_EXPIRES']
        else:
            access_token_expires = app.config['JWT_ACCESS_TOKEN_EXPIRES']
            #refresh_token_expires = app.config['JWT_REFRESH_TOKEN_EXPIRES']

        access_token = create_access_token(identity=str(user.id), expires_delta=access_token_expires)
        #refresh_token = create_access_token(identity=str(user.id), expires_delta=refresh_token_expires)

        response = make_response(jsonify({
            "message": "Logowanie pomyślne",
            "username": user.username,
            "email": user.email,
            "access_token": access_token,
            #"refresh_token": str(refresh_token),
            "expire_time": str(access_token_expires),
            #"refresh_expire_time": str(refresh_token_expires)
        }))

        response.set_cookie("access_token", access_token, httponly=False, samesite='Lax', secure=True)
        #response.set_cookie("refresh_token", refresh_token, httponly=False, samesite='Lax', secure=True)

        return response, 200
    
    return jsonify({"message": "Niepoprawne dane."}), 401

@app.route('/register', methods=['POST'])
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
        #refresh_token_expires = app.config['JWT_REFRESH_TOKEN_EXPIRES']

        access_token = create_access_token(identity=str(new_user.id), expires_delta=access_token_expires)
        #refresh_token = create_access_token(identity=str(new_user.id), expires_delta=refresh_token_expires)

        response = make_response(jsonify({
            "message": "Rejestracja pomyślna",
            "username": new_user.username,
            "email": new_user.email,
            "access_token": str(access_token),
            #"refresh_token": str(refresh_token),
            "expire_time": str(access_token_expires),
            #"refresh_expire_time": str(refresh_token_expires)
        }))

        response.set_cookie("access_token", access_token, httponly=False, samesite='Lax', secure=True)
        #response.set_cookie("refresh_token", refresh_token, httponly=False, samesite='Lax', secure=True)

        return response, 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Błąd podczas rejestracji: " + str(e)}), 500

# @app.route('/refresh', methods=['POST'])
# def refresh():
#     refresh_token = request.cookies.get("refresh_token")
#     if not refresh_token:
#         return jsonify({"message": "Brak tokena"}), 401

#     new_access_token = create_access_token(identity=get_jwt_identity())
#     response = make_response(jsonify({"message": "Token odświeżony."}))
#     response.set_cookie("access_token", new_access_token, httponly=False, samesite='Lax', secure=True)

#     return response, 200

if __name__ == '__main__':
    app.run(debug=True)