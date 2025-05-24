from models.book_collection import BookCollection
from models.wishlist import WishList
from models import db

def add_book_to_collection(user_id, data):
    existing_book = BookCollection.query.filter_by(isbn=data['isbn'], user_id=user_id).first()
    if existing_book:
        return None, "Książka o tym numerze ISBN już istnieje w kolekcji."
    new_book = BookCollection(user_id=user_id, **data)
    db.session.add(new_book)
    db.session.commit()
    return new_book, None

def add_book_to_wishlist(user_id, data):
    existing_book = WishList.query.filter_by(isbn=data['isbn'], user_id=user_id).first()
    if existing_book:
        return None, "Książka o tym numerze ISBN już istnieje na liście życzeń."
    new_book = WishList(user_id=user_id, **data)
    db.session.add(new_book)
    db.session.commit()
    return new_book, None

def get_books_for_user(user_id):
    return BookCollection.query.filter_by(user_id=user_id).all()

def get_wishlist_for_user(user_id):
    return WishList.query.filter_by(user_id=user_id).all()