from datetime import datetime
import os
from sqlite3 import IntegrityError
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import requests
from sqlalchemy import func
from models.user import User
from controllers.books_controller import add_book_to_collection, add_book_to_wishlist, get_books_for_user, get_wishlist_for_user
from models.book_collection import BookCollection
from models.wishlist import WishList
from models import db
from extensions import limiter

books_bp = Blueprint('booklist_bp', __name__)

@books_bp.route('/api/<string:username>/<string:type>', methods=['GET'])
@jwt_required()
def get_list(username, type):
    user = User.query.filter(func.lower(User.username) == username.lower()).first()
    if not user:
        return jsonify({"message": "Użytkownik nie istnieje."}), 404

    if type == 'bc':
        book_collection = get_books_for_user(user.id)
        book_collection_data = [book.to_dict() for book in book_collection]
        return jsonify(book_collection_data), 200
    elif type == 'wl':
        wish_list = get_wishlist_for_user(user.id)
        wish_list_data = [book.to_dict() for book in wish_list]
        return jsonify(wish_list_data), 200

@books_bp.route('/api/search-covers', methods=['GET'])
def search_covers():
    title = request.args.get('title', '')
    author = request.args.get('author', '')
    if not title and not author:
        return jsonify({"error": "Brak tytułu lub autora."}), 400

    query = f"{title} {author}".strip()
    try:
        search_url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'q': f"{query} książka",
            'key': os.getenv('GOOGLE_CS_API_KEY'),
            'cx': os.getenv('GOOGLE_CS_ID'),
            'searchType': 'image',
            'imgSize': 'large',
            'num': 10
        }
        response = requests.get(search_url, params=params)
        results = response.json()
        covers = []
        if 'items' in results:
            for item in results['items']:
                covers.append(item['link'])
        return jsonify(covers)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@books_bp.route('/api/add-book/<string:type>', methods=['POST'])
@limiter.exempt
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
            book, error = add_book_to_collection(user_id, data)
            if error:
                return jsonify({"error": error}), 400
            return jsonify({"message": "Książka dodana do kolekcji."}), 201
        elif type == 'wl':
            book, error = add_book_to_wishlist(user_id, data)
            if error:
                return jsonify({"error": error}), 400
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

@books_bp.route('/api/edit-book/<string:type>/<int:book_id>', methods=['PATCH'])
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

@books_bp.route('/api/review-book/<string:type>/<int:book_id>', methods=['PATCH'])
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

@books_bp.route('/api/book-details/<string:type>/<int:book_id>', methods=['GET'])
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

@books_bp.route('/api/book-exists/<string:type>/<int:book_id>', methods=['GET'])
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

@books_bp.route('/api/remove-all-books/<string:type>', methods=['DELETE'])
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

@books_bp.route('/api/remove-book/<string:type>/<int:book_id>', methods=['DELETE'])
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

@books_bp.route('/api/move-book-to/<string:type>//<int:book_id>', methods=['POST'])
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