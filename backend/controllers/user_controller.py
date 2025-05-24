from models import User, BookCollection, WishList, db
from sqlalchemy import func

def get_user_by_username(username):
    return User.query.filter(func.lower(User.username) == username.lower()).first()

def delete_user_and_data(user):
    BookCollection.query.filter_by(user_id=user.id).delete()
    WishList.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()

def get_all_users():
    return User.query.all()