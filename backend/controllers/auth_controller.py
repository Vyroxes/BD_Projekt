from sqlalchemy import func
from models import User, db
from flask_bcrypt import check_password_hash, generate_password_hash

def register_user(username, password):
    if User.query.filter_by(username=username).first():
        return None
    hashed_password = generate_password_hash(password).decode('utf-8')
    user = User(username=username, password=hashed_password)
    db.session.add(user)
    db.session.commit()
    return user

def authenticate_user(usernameOrEmail, password):
    user = User.query.filter(
        (func.lower(User.username) == func.lower(usernameOrEmail)) |
        (func.lower(User.email) == func.lower(usernameOrEmail))
    ).first()
    if user and check_password_hash(user.password, password):
        return user
    return None

def get_user_by_id(user_id):
    return User.query.get(user_id)